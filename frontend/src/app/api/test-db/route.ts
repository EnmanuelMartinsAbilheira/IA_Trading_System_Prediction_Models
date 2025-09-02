import { db } from '@/lib/db'

export async function GET() {
  try {
    // Test database connection by querying users
    const users = await db.user.findMany()
    
    return Response.json({
      success: true,
      message: 'Database connection successful',
      data: {
        userCount: users.length,
        users: users
      }
    })
  } catch (error) {
    console.error('Database connection error:', error)
    return Response.json({
      success: false,
      message: 'Database connection failed',
      error: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 })
  }
}