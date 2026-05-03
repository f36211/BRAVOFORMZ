import { NextRequest, NextResponse } from 'next/server'
import { getGlobalLeaderboard, getSubjectLeaderboard, getTopicLeaderboard } from '@/lib/db'

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const subjectId = searchParams.get('subjectId')
    const topicId = searchParams.get('topicId')
    const limit = parseInt(searchParams.get('limit') ?? '10', 10)

    let data
    
    if (subjectId && topicId) {
      // Topic-specific leaderboard
      data = await getTopicLeaderboard(subjectId, topicId, limit)
    } else if (subjectId) {
      // Subject-wide leaderboard
      data = await getSubjectLeaderboard(subjectId, limit)
    } else {
      // Global leaderboard
      data = await getGlobalLeaderboard(limit)
    }

    return NextResponse.json({ success: true, data })
  } catch (error) {
    console.error('[v0] Leaderboard fetch error:', error)
    return NextResponse.json(
      { success: false, error: 'Failed to fetch leaderboard' },
      { status: 500 }
    )
  }
}
