export type Question = {
  id: string
  text: string
  options: string[]
  optional?: boolean
}

export const questions: Question[] = [
  {
    id: "complaint",
    text: "Что вас беспокоит?",
    options: ["Головная боль", "Температура", "Боль в животе", "Кашель"],
  },
  {
    id: "duration",
    text: "Как давно вы заметили эти симптомы?",
    options: ["Сегодня", "Вчера", "Несколько дней", "Больше недели"],
  },
  {
    id: "details",
    text: "Хотите добавить что-нибудь ещё?",
    options: [],
    optional: true,
  },
]
