import { db } from '@/lib/db'
import { NextRequest } from 'next/server'

export async function GET() {
  try {
    const simulations = await db.simulation.findMany({
      include: {
        trades: {
          orderBy: { timestamp: 'desc' },
          take: 10
        }
      },
      orderBy: { startTime: 'desc' }
    })

    return Response.json({
      success: true,
      data: simulations
    })
  } catch (error) {
    console.error('Error fetching simulations:', error)
    return Response.json({
      success: false,
      message: 'Failed to fetch simulations',
      error: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { name, initialBalance = 10000, strategy, parameters } = body

    if (!name) {
      return Response.json({
        success: false,
        message: 'Simulation name is required'
      }, { status: 400 })
    }

    const simulation = await db.simulation.create({
      data: {
        name,
        initialBalance,
        currentBalance: initialBalance,
        status: 'running',
        strategy,
        parameters
      }
    })

    return Response.json({
      success: true,
      message: 'Simulation created successfully',
      data: simulation
    })
  } catch (error) {
    console.error('Error creating simulation:', error)
    return Response.json({
      success: false,
      message: 'Failed to create simulation',
      error: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 })
  }
}

export async function PUT(request: NextRequest) {
  try {
    const body = await request.json()
    const { id, status, currentBalance, endTime } = body

    if (!id) {
      return Response.json({
        success: false,
        message: 'Simulation ID is required'
      }, { status: 400 })
    }

    const simulation = await db.simulation.update({
      where: { id },
      data: {
        ...(status && { status }),
        ...(currentBalance !== undefined && { currentBalance }),
        ...(endTime && { endTime }),
        updatedAt: new Date()
      }
    })

    return Response.json({
      success: true,
      message: 'Simulation updated successfully',
      data: simulation
    })
  } catch (error) {
    console.error('Error updating simulation:', error)
    return Response.json({
      success: false,
      message: 'Failed to update simulation',
      error: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 })
  }
}