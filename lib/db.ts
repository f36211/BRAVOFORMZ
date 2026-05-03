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

// Get top scores for a specific topic
export async function getTopicLeaderboard(subjectId: string, topicId: string, limit = 10): Promise<LeaderboardWithRank[]> {
  const result = await sql`
    SELECT 
      *,
      RANK() OVER (ORDER BY score DESC, time_taken_seconds ASC NULLS LAST) as rank
    FROM leaderboard
    WHERE subject_id = ${subjectId} AND topic_id = ${topicId}
    ORDER BY score DESC, time_taken_seconds ASC NULLS LAST
    LIMIT ${limit}
  `
  return result as LeaderboardWithRank[]
}

// Get top scores for a specific subject (across all topics)
export async function getSubjectLeaderboard(subjectId: string, limit = 10): Promise<LeaderboardWithRank[]> {
  const result = await sql`
    WITH user_avg AS (
      SELECT 
        username,
        subject_id,
        AVG(score) as avg_score,
        SUM(correct_answers) as total_correct,
        SUM(total_questions) as total_questions,
        MAX(created_at) as last_activity
      FROM leaderboard
      WHERE subject_id = ${subjectId}
      GROUP BY username, subject_id
    )
    SELECT 
      username,
      subject_id,
      ROUND(avg_score::numeric, 1) as score,
      total_correct as correct_answers,
      total_questions,
      last_activity as created_at,
      RANK() OVER (ORDER BY avg_score DESC) as rank
    FROM user_avg
    ORDER BY avg_score DESC
    LIMIT ${limit}
  `
  return result as LeaderboardWithRank[]
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
        COUNT(DISTINCT subject_id) as subjects_attempted,
        COUNT(DISTINCT topic_id) as topics_completed,
        MAX(created_at) as last_activity
      FROM leaderboard
      GROUP BY username
    )
    SELECT 
      username,
      ROUND(avg_score::numeric, 1) as score,
      total_correct as correct_answers,
      total_questions,
      subjects_attempted,
      topics_completed,
      last_activity as created_at,
      RANK() OVER (ORDER BY avg_score DESC, total_correct DESC) as rank
    FROM user_stats
    ORDER BY avg_score DESC, total_correct DESC
    LIMIT ${limit}
  `
  return result as LeaderboardWithRank[]
}

// Get a user's rank for a specific topic
export async function getUserTopicRank(username: string, subjectId: string, topicId: string): Promise<number | null> {
  const result = await sql`
    WITH ranked AS (
      SELECT 
        username,
        RANK() OVER (ORDER BY score DESC, time_taken_seconds ASC NULLS LAST) as rank
      FROM leaderboard
      WHERE subject_id = ${subjectId} AND topic_id = ${topicId}
    )
    SELECT rank FROM ranked WHERE username = ${username}
  `
  return result[0]?.rank ?? null
}

// Get user's all-time stats
export async function getUserStats(username: string) {
  const result = await sql`
    SELECT 
      COUNT(DISTINCT subject_id) as subjects_attempted,
      COUNT(DISTINCT topic_id) as topics_completed,
      ROUND(AVG(score)::numeric, 1) as average_score,
      SUM(correct_answers) as total_correct,
      SUM(total_questions) as total_questions,
      MAX(score) as highest_score,
      MAX(created_at) as last_activity
    FROM leaderboard
    WHERE username = ${username}
  `
  return result[0] ?? null
}
