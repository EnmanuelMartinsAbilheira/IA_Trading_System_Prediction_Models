import { db } from '@/lib/db'
import { NextRequest } from 'next/server'

export async function GET() {
  try {
    const models = await db.predictionModel.findMany({
      orderBy: { createdAt: 'desc' }
    })
    
    return Response.json({
      success: true,
      data: models
    })
  } catch (error) {
    console.error('Error fetching models:', error)
    return Response.json({
      success: false,
      message: 'Failed to fetch models',
      error: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { name, type, version, accuracy, status, description, parameters } = body

    if (!name || !type || !version || accuracy === undefined || !status) {
      return Response.json({
        success: false,
        message: 'Missing required fields'
      }, { status: 400 })
    }

    const model = await db.predictionModel.create({
      data: {
        name,
        type,
        version,
        accuracy,
        status,
        description,
        parameters
      }
    })

    return Response.json({
      success: true,
      message: 'Model created successfully',
      data: model
    })
  } catch (error) {
    console.error('Error creating model:', error)
    return Response.json({
      success: false,
      message: 'Failed to create model',
      error: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 })
  }
}