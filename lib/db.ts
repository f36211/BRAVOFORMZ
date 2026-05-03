import { neon } from '@neondatabase/serverless'

// Use a placeholder if DATABASE_URL is missing to prevent build-time crashes
const databaseUrl = process.env.DATABASE_URL || 'postgres://placeholder:placeholder@localhost:5432/placeholder'
const sql = neon(databaseUrl)

export type LeaderboardEntry = {
  id: number
  username: string
  subject_id: string
  topic_id: string
  score: number
  correct_answers: number
  total_questions: number
  time_taken_seconds: number | null
  created_at: string
}

export type LeaderboardWithRank = LeaderboardEntry & {
  rank: number
  subject_name?: string
  topic_name?: string
  reactions?: { emoji: string; count: number }[]
}

// Submit or update a quiz score
export async function submitScore(data: {
  username: string
  subjectId: string
  topicId: string
  score: number
  correctAnswers: number
  totalQuestions: number
  timeTakenSeconds?: number
}): Promise<LeaderboardEntry> {
  // Ensure reactions table exists on first score submission
  await initReactionsTable()
  
  const result = await sql`
    INSERT INTO leaderboard (username, subject_id, topic_id, score, correct_answers, total_questions, time_taken_seconds)
    VALUES (${data.username}, ${data.subjectId}, ${data.topicId}, ${data.score}, ${data.correctAnswers}, ${data.totalQuestions}, ${data.timeTakenSeconds ?? null})
    ON CONFLICT (username, subject_id, topic_id)
    DO UPDATE SET 
      score = GREATEST(leaderboard.score, EXCLUDED.score),
      correct_answers = CASE WHEN EXCLUDED.score > leaderboard.score THEN EXCLUDED.correct_answers ELSE leaderboard.correct_answers END,
      total_questions = CASE WHEN EXCLUDED.score > leaderboard.score THEN EXCLUDED.total_questions ELSE leaderboard.total_questions END,
      time_taken_seconds = CASE WHEN EXCLUDED.score > leaderboard.score THEN EXCLUDED.time_taken_seconds ELSE leaderboard.time_taken_seconds END,
      created_at = CASE WHEN EXCLUDED.score > leaderboard.score THEN NOW() ELSE leaderboard.created_at END
    RETURNING *
  `
  return result[0] as LeaderboardEntry
}

// Get global leaderboard (all subjects)
export async function getGlobalLeaderboard(limit = 20): Promise<LeaderboardWithRank[]> {
  const result = await sql`
    WITH user_stats AS (
      SELECT 
        username,
        AVG(score) as avg_score,
        SUM(correct_answers) as total_correct,
        SUM(total_questions) as total_questions,
        MAX(created_at) as last_activity,
        COUNT(DISTINCT subject_id) as subjects_attempted,
        COUNT(DISTINCT topic_id) as topics_completed
      FROM leaderboard
      GROUP BY username
    ),
    user_reactions_agg AS (
      SELECT 
        to_user, 
        json_agg(json_build_object('emoji', emoji, 'count', count)) as reactions
      FROM (
        SELECT to_user, emoji, COUNT(*) as count
        FROM user_reactions
        GROUP BY to_user, emoji
      ) r
      GROUP BY to_user
    )
    SELECT 
      us.username,
      ROUND(us.avg_score::numeric, 1) as score,
      us.total_correct as correct_answers,
      us.total_questions,
      us.last_activity as created_at,
      us.subjects_attempted,
      us.topics_completed,
      RANK() OVER (ORDER BY us.avg_score DESC) as rank,
      COALESCE(ra.reactions, '[]'::json) as reactions
    FROM user_stats us
    LEFT JOIN user_reactions_agg ra ON us.username = ra.to_user
    ORDER BY us.avg_score DESC
    LIMIT ${limit}
  `
  return result as LeaderboardWithRank[]
}

// Get leaderboard for a specific subject
export async function getSubjectLeaderboard(subjectId: string, limit = 20): Promise<LeaderboardWithRank[]> {
  const result = await sql`
    WITH user_stats AS (
      SELECT 
        username,
        AVG(score) as avg_score,
        SUM(correct_answers) as total_correct,
        SUM(total_questions) as total_questions,
        MAX(created_at) as last_activity,
        COUNT(DISTINCT topic_id) as topics_completed
      FROM leaderboard
      WHERE subject_id = ${subjectId}
      GROUP BY username
    ),
    user_reactions_agg AS (
      SELECT 
        to_user, 
        json_agg(json_build_object('emoji', emoji, 'count', count)) as reactions
      FROM (
        SELECT to_user, emoji, COUNT(*) as count
        FROM user_reactions
        GROUP BY to_user, emoji
      ) r
      GROUP BY to_user
    )
    SELECT 
      us.username,
      ROUND(us.avg_score::numeric, 1) as score,
      us.total_correct as correct_answers,
      us.total_questions,
      us.last_activity as created_at,
      us.topics_completed,
      RANK() OVER (ORDER BY us.avg_score DESC) as rank,
      COALESCE(ra.reactions, '[]'::json) as reactions
    FROM user_stats us
    LEFT JOIN user_reactions_agg ra ON us.username = ra.to_user
    ORDER BY us.avg_score DESC
    LIMIT ${limit}
  `
  return result as LeaderboardWithRank[]
}

// Get leaderboard for a specific topic
export async function getTopicLeaderboard(subjectId: string, topicId: string, limit = 20): Promise<LeaderboardWithRank[]> {
  const result = await sql`
    WITH user_reactions_agg AS (
      SELECT 
        to_user, 
        json_agg(json_build_object('emoji', emoji, 'count', count)) as reactions
      FROM (
        SELECT to_user, emoji, COUNT(*) as count
        FROM user_reactions
        GROUP BY to_user, emoji
      ) r
      GROUP BY to_user
    )
    SELECT 
      l.username,
      l.score,
      l.correct_answers,
      l.total_questions,
      l.created_at,
      RANK() OVER (ORDER BY l.score DESC, l.time_taken_seconds ASC NULLS LAST) as rank,
      COALESCE(ra.reactions, '[]'::json) as reactions
    FROM leaderboard l
    LEFT JOIN user_reactions_agg ra ON l.username = ra.to_user
    WHERE l.subject_id = ${subjectId} AND l.topic_id = ${topicId}
    ORDER BY l.score DESC, l.time_taken_seconds ASC NULLS LAST
    LIMIT ${limit}
  `
  return result as LeaderboardWithRank[]
}

// Get user stats for a specific user
export async function getUserStats(username: string) {
  const result = await sql`
    SELECT 
      COUNT(DISTINCT topic_id) as topics_completed,
      COUNT(DISTINCT subject_id) as subjects_attempted,
      ROUND(AVG(score)::numeric, 1) as average_score,
      MAX(score) as highest_score,
      SUM(correct_answers) as total_correct,
      SUM(total_questions) as total_questions,
      SUM(time_taken_seconds) as total_time_seconds
    FROM leaderboard
    WHERE username = ${username}
  `
  return result[0]
}

// Get rank of a user for a specific topic
export async function getUserTopicRank(username: string, subjectId: string, topicId: string) {
  const result = await sql`
    SELECT rank FROM (
      SELECT 
        username,
        RANK() OVER (ORDER BY score DESC, time_taken_seconds ASC NULLS LAST) as rank
      FROM leaderboard
      WHERE subject_id = ${subjectId} AND topic_id = ${topicId}
    ) r
    WHERE username = ${username}
  `
  return result[0]?.rank || null
}

// Create reactions table if it doesn't exist (Efficient approach)
export async function initReactionsTable() {
  await sql`
    CREATE TABLE IF NOT EXISTS user_reactions (
      id SERIAL PRIMARY KEY,
      from_user TEXT NOT NULL,
      to_user TEXT NOT NULL,
      emoji TEXT NOT NULL,
      created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    )
  `
}

// Send a reaction (emoji) to another user
export async function sendReaction(fromUser: string, toUser: string, emoji: string) {
  // Limit one reaction type per sender-receiver to keep DB small
  const result = await sql`
    INSERT INTO user_reactions (from_user, to_user, emoji)
    VALUES (${fromUser}, ${toUser}, ${emoji})
    RETURNING *
  `
  return result[0]
}

// Get recent reactions for a user
export async function getRecentReactions(username: string, limit = 5) {
  return await sql`
    SELECT from_user, emoji, created_at
    FROM user_reactions
    WHERE to_user = ${username}
    ORDER BY created_at DESC
    LIMIT ${limit}
  `
}

// Get reaction counts for a user (efficient aggregation)
export async function getReactionCounts(username: string) {
  const result = await sql`
    SELECT emoji, COUNT(*) as count
    FROM user_reactions
    WHERE to_user = ${username}
    GROUP BY emoji
  `
  return result
}
