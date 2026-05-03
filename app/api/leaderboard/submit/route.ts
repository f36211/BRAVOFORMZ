import { NextRequest, NextResponse } from 'next/server'
import { submitScore, getUserTopicRank } from '@/lib/db'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    const { username, subjectId, topicId, score, correctAnswers, totalQuestions, timeTakenSeconds } = body

    if (!username || !subjectId || !topicId || score === undefined) {
      return NextResponse.json(
        { success: false, error: 'Missing required fields' },
        { status: 400 }
      )
    }

    // Submit the score
    const entry = await submitScore({
      username,
      subjectId,
      topicId,
      score,
      correctAnswers,
      totalQuestions,
      timeTakenSeconds,
    })

    // Get the user's rank for this topic
    const rank = await getUserTopicRank(username, subjectId, topicId)

    return NextResponse.json({ 
      success: true, 
      data: { 
        ...entry, 
        rank 
      } 
    })
  } catch (error) {
    console.error('[v0] Score submit error:', error)
    return NextResponse.json(
      { success: false, error: 'Failed to submit score' },
      { status: 500 }
    )
  }
}
