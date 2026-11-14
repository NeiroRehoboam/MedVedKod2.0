import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"
import { mockQuestions } from "@/data/questions.mock"
import { Typography } from "@maxhub/max-ui"

export function ReferencesPage() {
  return (
    <div className="mx-auto w-full max-w-3xl px-6">
      {/* Заголовок */}
      <section className="mb-10">
        <Typography.Title
          variant="large-strong"
          className="font-unbounded! text-4xl!"
        >
          Что вас
          <br />
          беспокоит?
        </Typography.Title>

        <p className="mt-4">
          <Typography.Text variant="body" color="secondary">
            Собрали ответы на самые частые вопросы о МедВеде. Возможно, здесь
            уже есть то, что вы ищете.
          </Typography.Text>
        </p>
      </section>

      {/* Частые вопросы */}
      <section>
        <Accordion className={"bg-max-secondary"}>
          {mockQuestions.map((item) => (
            <AccordionItem key={item.id} value={item.id}>
              <AccordionTrigger className="text-base">
                <Typography.Title>{item.question}</Typography.Title>
              </AccordionTrigger>

              <AccordionContent>
                <Typography.Text variant="body" color="primary">
                  {item.answer}
                </Typography.Text>
              </AccordionContent>
            </AccordionItem>
          ))}

          <AccordionItem value="support">
            <AccordionTrigger className="text-base">
              Остались вопросы?
            </AccordionTrigger>

            <AccordionContent>
              <p>
                Не нашли нужный ответ? Напишите нам - мы постараемся помочь.
              </p>

              <div>
                <a href="mailto:support@example.com">support@example.com</a>
              </div>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </section>
    </div>
  )
}
