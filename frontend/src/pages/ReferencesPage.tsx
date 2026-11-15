import { PageDescription, PageTitle } from "@/components/common"
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"
import { mockQuestions } from "@/data/questions.mock"

export function ReferencesPage() {
  return (
    <div>
      {/* Заголовок */}
      <section className="mb-8 space-y-5">
        <PageTitle as="h1">
          Что вас
          <br />
          беспокоит?
        </PageTitle>

        <PageDescription>
          Собрали ответы на самые частые вопросы о МедВеде. Возможно, здесь уже
          есть то, что вы ищете.
        </PageDescription>
      </section>

      {/* Частые вопросы */}
      <section>
        <Accordion className="rounded-max-medium bg-max-secondary">
          {mockQuestions.map((item) => (
            <AccordionItem key={item.id} value={item.id}>
              <AccordionTrigger className="text-base">
                {item.question}
              </AccordionTrigger>

              <AccordionContent>{item.answer}</AccordionContent>
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
