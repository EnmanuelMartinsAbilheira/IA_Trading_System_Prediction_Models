import { db } from '@/lib/db'

export interface SimulationConfig {
  name: string
  initialBalance: number
  symbol: string
  strategy: string
  parameters: Record<string, any>
}

export interface TradeSignal {
  symbol: string
  type: 'buy' | 'sell'
  quantity: number
  price: number
  confidence: number
  reasoning: string
}

export class TradingSimulator {
  private simulationId: string
  private config: SimulationConfig
  private isRunning: boolean = false
  private currentBalance: number
  private positions: Map<string, { quantity: number; avgPrice: number }> = new Map()

  constructor(simulationId: string, config: SimulationConfig) {
    this.simulationId = simulationId
    this.config = config
    this.currentBalance = config.initialBalance
  }

  async start() {
    this.isRunning = true
    
    // Update simulation status
    await db.simulation.update({
      where: { id: this.simulationId },
      data: { status: 'running' }
    })

    console.log(`Simulation ${this.simulationId} started`)
    
    // Start simulation loop
    this.simulationLoop()
  }

  async stop() {
    this.isRunning = false
    
    // Update simulation status
    await db.simulation.update({
      where: { id: this.simulationId },
      data: { 
        status: 'stopped',
        endTime: new Date(),
        currentBalance: this.currentBalance
      }
    })

    console.log(`Simulation ${this.simulationId} stopped`)
  }

  private async simulationLoop() {
    while (this.isRunning) {
      try {
        await this.executeSimulationStep()
        await new Promise(resolve => setTimeout(resolve, 5000)) // Run every 5 seconds
      } catch (error) {
        console.error('Simulation step error:', error)
      }
    }
  }

  private async executeSimulationStep() {
    // Get latest trading data
    const latestData = await db.tradingData.findFirst({
      where: { symbol: this.config.symbol },
      orderBy: { timestamp: 'desc' }
    })

    if (!latestData) {
      console.log('No trading data available')
      return
    }

    // Generate trading signal based on strategy
    const signal = await this.generateSignal(latestData)
    
    if (signal) {
      await this.executeTrade(signal)
    }

    // Update simulation metrics
    await this.updateMetrics()
  }

  private async generateSignal(data: any): Promise<TradeSignal | null> {
    const currentPrice = data.close
    const strategy = this.config.strategy

    switch (strategy) {
      case 'momentum':
        return this.momentumStrategy(data)
      case 'mean_reversion':
        return this.meanReversionStrategy(data)
      case 'ai_prediction':
        return await this.aiPredictionStrategy(data)
      default:
        return null
    }
  }

  private momentumStrategy(data: any): TradeSignal | null {
    const currentPrice = data.close
    const previousPrice = data.open
    const priceChange = (currentPrice - previousPrice) / previousPrice
    
    const threshold = 0.01 // 1% threshold
    
    if (priceChange > threshold) {
      return {
        symbol: this.config.symbol,
        type: 'buy',
        quantity: Math.floor(this.currentBalance * 0.1 / currentPrice),
        price: currentPrice,
        confidence: Math.min(priceChange * 10, 0.9),
        reasoning: 'Momentum: Price increasing'
      }
    } else if (priceChange < -threshold) {
      return {
        symbol: this.config.symbol,
        type: 'sell',
        quantity: Math.floor(this.currentBalance * 0.1 / currentPrice),
        price: currentPrice,
        confidence: Math.min(Math.abs(priceChange) * 10, 0.9),
        reasoning: 'Momentum: Price decreasing'
      }
    }
    
    return null
  }

  private meanReversionStrategy(data: any): TradeSignal | null {
    const currentPrice = data.close
    const high = data.high
    const low = data.low
    const midPoint = (high + low) / 2
    
    const deviation = (currentPrice - midPoint) / midPoint
    const threshold = 0.02 // 2% threshold
    
    if (deviation > threshold) {
      return {
        symbol: this.config.symbol,
        type: 'sell',
        quantity: Math.floor(this.currentBalance * 0.1 / currentPrice),
        price: currentPrice,
        confidence: Math.min(deviation * 5, 0.9),
        reasoning: 'Mean Reversion: Price above mean'
      }
    } else if (deviation < -threshold) {
      return {
        symbol: this.config.symbol,
        type: 'buy',
        quantity: Math.floor(this.currentBalance * 0.1 / currentPrice),
        price: currentPrice,
        confidence: Math.min(Math.abs(deviation) * 5, 0.9),
        reasoning: 'Mean Reversion: Price below mean'
      }
    }
    
    return null
  }

  private async aiPredictionStrategy(data: any): Promise<TradeSignal | null> {
    try {
      // Get the most accurate AI model
      const model = await db.predictionModel.findFirst({
        where: { status: 'active' },
        orderBy: { accuracy: 'desc' }
      })

      if (!model) return null

      // Make prediction
      const response = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL || ''}/api/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          modelId: model.id,
          symbol: this.config.symbol,
          timeframe: '1h'
        })
      })

      const result = await response.json()
      
      if (result.success && result.data?.prediction) {
        const prediction = result.data.prediction
        const currentPrice = data.close
        const predictedPrice = prediction.prediction
        const priceChange = (predictedPrice - currentPrice) / currentPrice
        
        if (Math.abs(priceChange) > 0.005 && prediction.confidence > 0.6) {
          return {
            symbol: this.config.symbol,
            type: priceChange > 0 ? 'buy' : 'sell',
            quantity: Math.floor(this.currentBalance * 0.1 / currentPrice),
            price: currentPrice,
            confidence: prediction.confidence,
            reasoning: `AI Prediction: ${prediction.direction} with ${prediction.confidence} confidence`
          }
        }
      }
    } catch (error) {
      console.error('AI prediction strategy error:', error)
    }
    
    return null
  }

  private async executeTrade(signal: TradeSignal) {
    const tradeValue = signal.quantity * signal.price
    
    if (signal.type === 'buy' && tradeValue > this.currentBalance) {
      console.log('Insufficient balance for buy trade')
      return
    }

    // Execute trade
    const trade = await db.trade.create({
      data: {
        symbol: signal.symbol,
        type: signal.type,
        quantity: signal.quantity,
        price: signal.price,
        status: 'executed',
        strategy: this.config.strategy,
        simulationId: this.simulationId
      }
    })

    // Update balance and positions
    if (signal.type === 'buy') {
      this.currentBalance -= tradeValue
      const currentPos = this.positions.get(signal.symbol) || { quantity: 0, avgPrice: 0 }
      const totalQuantity = currentPos.quantity + signal.quantity
      const totalValue = (currentPos.quantity * currentPos.avgPrice) + tradeValue
      currentPos.avgPrice = totalValue / totalQuantity
      currentPos.quantity = totalQuantity
      this.positions.set(signal.symbol, currentPos)
    } else {
      this.currentBalance += tradeValue
      const currentPos = this.positions.get(signal.symbol)
      if (currentPos) {
        currentPos.quantity -= signal.quantity
        if (currentPos.quantity <= 0) {
          this.positions.delete(signal.symbol)
        }
      }
    }

    console.log(`Executed ${signal.type} trade: ${signal.quantity} @ ${signal.price}`)
  }

  private async updateMetrics() {
    // Calculate total portfolio value
    let portfolioValue = this.currentBalance
    
    for (const [symbol, position] of this.positions) {
      const latestData = await db.tradingData.findFirst({
        where: { symbol },
        orderBy: { timestamp: 'desc' }
      })
      
      if (latestData) {
        portfolioValue += position.quantity * latestData.close
      }
    }

    // Get all trades for this simulation
    const trades = await db.trade.findMany({
      where: { simulationId: this.simulationId }
    })

    // Calculate win rate
    const completedTrades = trades.filter(trade => trade.profitLoss !== null)
    const winRate = completedTrades.length > 0 
      ? completedTrades.filter(trade => (trade.profitLoss || 0) > 0).length / completedTrades.length 
      : 0

    // Calculate profit/loss
    const profitLoss = portfolioValue - this.config.initialBalance

    // Update simulation
    await db.simulation.update({
      where: { id: this.simulationId },
      data: {
        currentBalance: portfolioValue,
        totalTrades: trades.length,
        winRate: winRate,
        profitLoss: profitLoss
      }
    })
  }

  getStatus() {
    return {
      isRunning: this.isRunning,
      currentBalance: this.currentBalance,
      positions: Object.fromEntries(this.positions)
    }
  }
}

// Factory function to create and start a simulation
export async function createAndStartSimulation(config: SimulationConfig): Promise<string> {
  const simulation = await db.simulation.create({
    data: {
      name: config.name,
      initialBalance: config.initialBalance,
      currentBalance: config.initialBalance,
      status: 'running',
      strategy: config.strategy,
      parameters: config.parameters
    }
  })

  const simulator = new TradingSimulator(simulation.id, config)
  simulator.start()

  return simulation.id
}