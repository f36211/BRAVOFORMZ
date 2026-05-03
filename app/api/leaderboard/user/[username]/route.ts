import { NextRequest, NextResponse } from 'next/server'
import { getUserStats } from '@/lib/db'

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ username: string }> }
) {
  try {
    const { username } = await params

    if (!username) {
      return NextResponse.json(
        { success: false, error: 'Username is required' },
        { status: 400 }
      )
    }

    const stats = await getUserStats(username)

    return NextResponse.json({ success: true, data: stats })
  } catch (error) {
    console.error('[v0] User stats fetch error:', error)
    return NextResponse.json(
      { success: false, error: 'Failed to fetch user stats' },
      { status: 500 }
    )
  }
}
