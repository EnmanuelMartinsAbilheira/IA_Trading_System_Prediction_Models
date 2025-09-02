import { db } from '@/lib/db'
import { NextRequest } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const symbol = searchParams.get('symbol')
    const limit = parseInt(searchParams.get('limit') || '50')
    const offset = parseInt(searchParams.get('offset') || '0')

    if (!symbol) {
      return Response.json({
        success: false,
        message: 'Symbol parameter is required'
      }, { status: 400 })
    }

    const tradingData = await db.tradingData.findMany({
      where: { symbol },
      orderBy: { timestamp: 'desc' },
      take: limit,
      skip: offset
    })

    const totalCount = await db.tradingData.count({
      where: { symbol }
    })

    return Response.json({
      success: true,
      data: {
        tradingData,
        pagination: {
          total: totalCount,
          limit,
          offset,
          hasMore: offset + limit < totalCount
        }
      }
    })
  } catch (error) {
    console.error('Error fetching trading data:', error)
    return Response.json({
      success: false,
      message: 'Failed to fetch trading data',
      error: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { symbol, open, high, low, close, volume, interval = '1h' } = body

    if (!symbol || open === undefined || high === undefined || 
        low === undefined || close === undefined || volume === undefined) {
      return Response.json({
        success: false,
        message: 'Missing required fields: symbol, open, high, low, close, volume'
      }, { status: 400 })
    }

    const tradingData = await db.tradingData.create({
      data: {
        symbol,
        open,
        high,
        low,
        close,
        volume,
        interval,
        timestamp: new Date()
      }
    })

    return Response.json({
      success: true,
      message: 'Trading data created successfully',
      data: tradingData
    })
  } catch (error) {
    console.error('Error creating trading data:', error)
    return Response.json({
      success: false,
      message: 'Failed to create trading data',
      error: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 })
  }
}