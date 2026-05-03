import { NextRequest, NextResponse } from 'next/server'
import { sendReaction } from '@/lib/db'

export async function POST(request: NextRequest) {
  try {
    const { fromUser, toUser, emoji } = await request.json()

    if (!fromUser || !toUser || !emoji) {
      return NextResponse.json(
        { success: false, error: 'Missing required fields' },
        { status: 400 }
      )
    }

    const reaction = await sendReaction(fromUser, toUser, emoji)

    return NextResponse.json({ success: true, data: reaction })
  } catch (error) {
    console.error('[v0] Reaction error:', error)
    return NextResponse.json(
      { success: false, error: 'Failed to send reaction' },
      { status: 500 }
    )
  }
}
