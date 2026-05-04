export type ContentBlock =
  | { type: "heading"; text: string; level?: 1 | 2 | 3 }
  | { type: "text"; text: string }
  | { type: "quote"; text: string; translation?: string }
  | { type: "highlight"; text: string }
  | { type: "list"; items: string[]; ordered?: boolean }
  | { type: "table"; headers: string[]; rows: string[][] }
  | { type: "math"; tex: string; display?: boolean }
  | { type: "chart"; chartType: "bar" | "line" | "area"; data: { name: string; value: number }[] }
  | { type: "simulation"; simType: "atom" | "cells" | "newton" | "circuit" | "magnet" | "wave" | "piston" | "geometry" }
  | { type: "image"; url: string; caption?: string }

export type Lesson = {
  id: string
  title: string
  estMinutes?: number
  content: ContentBlock[]
}

export type Flashcard = {
  id: string
  question: string
  answer: string
}

export type QuizQuestion = {
  id: string
  type: "multiple_choice"
  question: string
  options: string[]
  answer: number
  explanation?: string
}

export type Quiz = {
  questions: QuizQuestion[]
}

export type Topic = {
  id: string
  title: string
  description: string
  bookmarked?: boolean
  lessons: Lesson[]
  flashcards: Flashcard[]
  quiz: Quiz
}

export type Subject = {
  id: string
  name: string
  description: string
  grade: number[]
  icon: string
  image?: string
  color: "neutral" | "mono" | "soft"
  topics: Topic[]
}

export type AppData = {
  app: {
    name: string
    class: string
    version: string
  }
  subjects: Subject[]
}

export type SearchResult =
  | { kind: "subject"; subjectId: string; title: string; subtitle: string }
  | { kind: "topic"; subjectId: string; topicId: string; title: string; subtitle: string }
  | { kind: "lesson"; subjectId: string; topicId: string; lessonId: string; title: string; subtitle: string }
  | {
      kind: "flashcard"
      subjectId: string
      topicId: string
      flashcardId: string
      title: string
      subtitle: string
    }
