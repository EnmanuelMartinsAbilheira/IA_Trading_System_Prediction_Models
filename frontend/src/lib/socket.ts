import { Server } from 'socket.io'
import { db } from '@/lib/db'

interface TradingDataUpdate {
  symbol: string
  price: number
  change: number
  changePercent: number
  volume: number
  timestamp: string
}

interface PredictionUpdate {
  modelId: string
  symbol: string
  prediction: number
  confidence: number
  direction: string
  timestamp: string
}

interface SimulationUpdate {
  simulationId: string
  status: string
  currentBalance: number
  profitLoss: number
  tradeCount: number
  timestamp: string
}

export const setupSocket = (io: Server) => {
  // Store room subscriptions
  const subscriptions = new Map<string, Set<string>>()

  io.on('connection', (socket) => {
    console.log('Client connected:', socket.id)

    // Handle room subscriptions for real-time data
    socket.on('subscribe', (data: { room: string }) => {
      const { room } = data
      
      // Join room
      socket.join(room)
      
      // Track subscription
      if (!subscriptions.has(room)) {
        subscriptions.set(room, new Set())
      }
      subscriptions.get(room)!.add(socket.id)
      
      console.log(`Client ${socket.id} subscribed to room: ${room}`)
      
      // Send initial data for the room
      sendInitialData(socket, room)
    })

    socket.on('unsubscribe', (data: { room: string }) => {
      const { room } = data
      
      // Leave room
      socket.leave(room)
      
      // Remove from tracking
      if (subscriptions.has(room)) {
        subscriptions.get(room)!.delete(socket.id)
        if (subscriptions.get(room)!.size === 0) {
          subscriptions.delete(room)
        }
      }
      
      console.log(`Client ${socket.id} unsubscribed from room: ${room}`)
    })

    // Handle prediction requests
    socket.on('request_prediction', async (data: { modelId: string; symbol: string }) => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL || ''}/api/predict`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        })
        
        const result = await response.json()
        
        socket.emit('prediction_result', {
          success: result.success,
          data: result.data,
          timestamp: new Date().toISOString()
        })
      } catch (error) {
        socket.emit('prediction_result', {
          success: false,
          error: error instanceof Error ? error.message : 'Unknown error',
          timestamp: new Date().toISOString()
        })
      }
    })

    // Handle simulation control
    socket.on('simulation_control', async (data: { action: string; config?: any }) => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL || ''}/api/simulator`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        })
        
        const result = await response.json()
        
        socket.emit('simulation_response', {
          success: result.success,
          data: result.data,
          timestamp: new Date().toISOString()
        })
      } catch (error) {
        socket.emit('simulation_response', {
          success: false,
          error: error instanceof Error ? error.message : 'Unknown error',
          timestamp: new Date().toISOString()
        })
      }
    })

    // Handle trading data requests
    socket.on('request_trading_data', async (data: { symbol: string; limit?: number }) => {
      try {
        const params = new URLSearchParams({
          symbol: data.symbol,
          limit: (data.limit || 50).toString()
        })
        
        const response = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL || ''}/api/trading-data?${params}`)
        const result = await response.json()
        
        socket.emit('trading_data_response', {
          success: result.success,
          data: result.data,
          timestamp: new Date().toISOString()
        })
      } catch (error) {
        socket.emit('trading_data_response', {
          success: false,
          error: error instanceof Error ? error.message : 'Unknown error',
          timestamp: new Date().toISOString()
        })
      }
    })

    // Handle legacy message format for backward compatibility
    socket.on('message', (msg: { text: string; senderId: string }) => {
      socket.emit('message', {
        text: `Echo: ${msg.text}`,
        senderId: 'system',
        timestamp: new Date().toISOString(),
      })
    })

    // Handle disconnect
    socket.on('disconnect', () => {
      console.log('Client disconnected:', socket.id)
      
      // Clean up subscriptions
      for (const [room, clients] of subscriptions.entries()) {
        clients.delete(socket.id)
        if (clients.size === 0) {
          subscriptions.delete(room)
        }
      }
    })

    // Send welcome message
    socket.emit('message', {
      text: 'Welcome to AI Trading System WebSocket!',
      senderId: 'system',
      timestamp: new Date().toISOString(),
    })
  })

  // Start real-time data feeds
  startDataFeeds(io, subscriptions)
}

async function sendInitialData(socket: any, room: string) {
  try {
    switch (room) {
      case 'trading-data':
        const tradingData = await db.tradingData.findMany({
          orderBy: { timestamp: 'desc' },
          take: 10
        })
        socket.emit('trading_data_update', {
          type: 'initial',
          data: tradingData,
          timestamp: new Date().toISOString()
        })
        break

      case 'predictions':
        const predictions = await db.prediction.findMany({
          include: {
            model: true,
            tradingData: true
          },
          orderBy: { createdAt: 'desc' },
          take: 10
        })
        socket.emit('prediction_update', {
          type: 'initial',
          data: predictions,
          timestamp: new Date().toISOString()
        })
        break

      case 'simulations':
        const simulations = await db.simulation.findMany({
          orderBy: { startTime: 'desc' },
          take: 10
        })
        socket.emit('simulation_update', {
          type: 'initial',
          data: simulations,
          timestamp: new Date().toISOString()
        })
        break
    }
  } catch (error) {
    console.error('Error sending initial data:', error)
  }
}

function startDataFeeds(io: Server, subscriptions: Map<string, Set<string>>) {
  // Simulate real-time trading data updates
  setInterval(async () => {
    if (subscriptions.has('trading-data')) {
      try {
        // Generate simulated trading data update
        const symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA']
        const symbol = symbols[Math.floor(Math.random() * symbols.length)]
        
        const latestData = await db.tradingData.findFirst({
          where: { symbol },
          orderBy: { timestamp: 'desc' }
        })

        if (latestData) {
          const change = (Math.random() - 0.5) * 0.02 // ±1% change
          const newPrice = latestData.close * (1 + change)
          
          const update: TradingDataUpdate = {
            symbol,
            price: newPrice,
            change: newPrice - latestData.close,
            changePercent: change * 100,
            volume: Math.floor(Math.random() * 1000000) + 500000,
            timestamp: new Date().toISOString()
          }

          io.to('trading-data').emit('trading_data_update', {
            type: 'update',
            data: update,
            timestamp: new Date().toISOString()
          })
        }
      } catch (error) {
        console.error('Error generating trading data update:', error)
      }
    }
  }, 3000) // Update every 3 seconds

  // Simulate prediction updates
  setInterval(async () => {
    if (subscriptions.has('predictions')) {
      try {
        // Get a random active model
        const model = await db.predictionModel.findFirst({
          where: { status: 'active' },
          orderBy: { createdAt: 'desc' }
        })

        if (model) {
          const symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA']
          const symbol = symbols[Math.floor(Math.random() * symbols.length)]
          
          const update: PredictionUpdate = {
            modelId: model.id,
            symbol,
            prediction: 100 + Math.random() * 50,
            confidence: 0.6 + Math.random() * 0.3,
            direction: Math.random() > 0.5 ? 'up' : 'down',
            timestamp: new Date().toISOString()
          }

          io.to('predictions').emit('prediction_update', {
            type: 'update',
            data: update,
            timestamp: new Date().toISOString()
          })
        }
      } catch (error) {
        console.error('Error generating prediction update:', error)
      }
    }
  }, 5000) // Update every 5 seconds

  // Simulate simulation updates
  setInterval(async () => {
    if (subscriptions.has('simulations')) {
      try {
        const runningSimulations = await db.simulation.findMany({
          where: { status: 'running' }
        })

        for (const simulation of runningSimulations) {
          const profitLoss = (Math.random() - 0.5) * 100
          const update: SimulationUpdate = {
            simulationId: simulation.id,
            status: simulation.status,
            currentBalance: simulation.currentBalance + profitLoss,
            profitLoss: simulation.profitLoss! + profitLoss,
            tradeCount: simulation.totalTrades + Math.floor(Math.random() * 3),
            timestamp: new Date().toISOString()
          }

          io.to('simulations').emit('simulation_update', {
            type: 'update',
            data: update,
            timestamp: new Date().toISOString()
          })
        }
      } catch (error) {
        console.error('Error generating simulation update:', error)
      }
    }
  }, 4000) // Update every 4 seconds
}