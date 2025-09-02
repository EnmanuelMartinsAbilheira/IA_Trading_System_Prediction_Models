import { db } from '@/lib/db'

async function main() {
  console.log('Seeding database...')

  // Create prediction models
  const models = await Promise.all([
    db.predictionModel.create({
      data: {
        name: 'LSTM Model v1',
        type: 'LSTM',
        version: '1.0.0',
        accuracy: 0.87,
        status: 'active',
        description: 'Long Short-Term Memory neural network for price prediction',
        parameters: {
          layers: 3,
          units: 128,
          dropout: 0.2,
          epochs: 100
        }
      }
    }),
    db.predictionModel.create({
      data: {
        name: 'Transformer v2',
        type: 'Transformer',
        version: '2.0.0',
        accuracy: 0.92,
        status: 'training',
        description: 'Transformer-based model with attention mechanism',
        parameters: {
          layers: 6,
          heads: 8,
          dModel: 512,
          dropout: 0.1
        }
      }
    }),
    db.predictionModel.create({
      data: {
        name: 'Ensemble Model v1',
        type: 'Ensemble',
        version: '1.0.0',
        accuracy: 0.89,
        status: 'active',
        description: 'Ensemble combining LSTM and Transformer predictions',
        parameters: {
          models: ['LSTM', 'Transformer'],
          weights: [0.4, 0.6],
          combination: 'weighted_average'
        }
      }
    })
  ])

  // Create sample trading data for AAPL
  const basePrice = 150
  const tradingData = []
  for (let i = 0; i < 20; i++) {
    const timestamp = new Date(Date.now() - (19 - i) * 60 * 60 * 1000) // Hourly data
    const volatility = 0.02
    const change = (Math.random() - 0.5) * volatility
    const price = basePrice * (1 + change * i / 10)
    
    tradingData.push({
      symbol: 'AAPL',
      timestamp,
      open: price * (1 - Math.random() * 0.01),
      high: price * (1 + Math.random() * 0.02),
      low: price * (1 - Math.random() * 0.02),
      close: price,
      volume: Math.floor(Math.random() * 1000000) + 500000,
      interval: '1h'
    })
  }

  await db.tradingData.createMany({
    data: tradingData
  })

  console.log('Database seeded successfully!')
  console.log(`Created ${models.length} prediction models`)
  console.log(`Created ${tradingData.length} trading data entries`)
}

main()
  .catch((e) => {
    console.error(e)
    process.exit(1)
  })
  .finally(async () => {
    await db.$disconnect()
  })