import { NextRequest } from 'next/server'
import { createAndStartSimulation } from '@/lib/simulator'

const activeSimulators = new Map<string, any>()

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { action, simulationId, config } = body

    switch (action) {
      case 'start':
        if (!config) {
          return Response.json({
            success: false,
            message: 'Configuration is required for starting simulation'
          }, { status: 400 })
        }

        const newSimulationId = await createAndStartSimulation(config)
        return Response.json({
          success: true,
          message: 'Simulation started successfully',
          data: { simulationId: newSimulationId }
        })

      case 'stop':
        if (!simulationId) {
          return Response.json({
            success: false,
            message: 'Simulation ID is required'
          }, { status: 400 })
        }

        const simulator = activeSimulators.get(simulationId)
        if (simulator) {
          await simulator.stop()
          activeSimulators.delete(simulationId)
        }

        return Response.json({
          success: true,
          message: 'Simulation stopped successfully'
        })

      default:
        return Response.json({
          success: false,
          message: 'Invalid action'
        }, { status: 400 })
    }
  } catch (error) {
    console.error('Simulator error:', error)
    return Response.json({
      success: false,
      message: 'Failed to process simulator action',
      error: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 })
  }
}

export async function GET() {
  try {
    const activeSimulations = Array.from(activeSimulators.keys())
    
    return Response.json({
      success: true,
      data: {
        activeSimulations,
        count: activeSimulations.length
      }
    })
  } catch (error) {
    console.error('Error fetching simulator status:', error)
    return Response.json({
      success: false,
      message: 'Failed to fetch simulator status',
      error: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 })
  }
}