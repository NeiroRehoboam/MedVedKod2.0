import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"
import { mockQuestions } from "@/data/questions.mock"

export function ReferencesPage() {
  return (
    <div className="mx-auto w-full max-w-3xl px-6">
      {/* Заголовок */}
      <section className="mb-10">
        <h1 className="font-unbounded text-4xl leading-[1.12] font-medium tracking-[-0.065em]">
          Помощь
          <br />и ответы
        </h1>

        <p className="mt-4 max-w-md text-muted-foreground">
          Собрали ответы на самые частые вопросы о МедВед. Возможно, здесь уже
          есть то, что вы ищете.
        </p>
      </section>

      {/* Частые вопросы */}
      <section>
        <Accordion>
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
