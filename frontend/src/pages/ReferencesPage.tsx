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
      <section className="mb-8 space-y-5">
        <PageTitle as="h1">Частые вопросы</PageTitle>

        <PageDescription>
          Собрали ответы на самые частые вопросы о МедВеде. Возможно, здесь уже
          есть то, что вы ищете.
        </PageDescription>
      </section>

      <section>
        <Accordion defaultValue={["plans"]} className={"border-0"}>
          {mockQuestions.map((item) => (
            <AccordionItem
              key={item.id}
              value={item.id}
              className="border-max-tertiary! bg-transparent! p-0 data-open:bg-transparent!"
            >
              <AccordionTrigger className="p-0 py-4 text-base font-medium hover:no-underline">
                {item.question}
              </AccordionTrigger>

              <AccordionContent>{item.answer}</AccordionContent>
            </AccordionItem>
          ))}

          <AccordionItem
            value="support"
            className="border-max-tertiary! bg-transparent! p-0 data-open:bg-transparent!"
          >
            <AccordionTrigger className="px-0 py-4 text-base font-medium hover:no-underline">
              Остались вопросы?
            </AccordionTrigger>

            <AccordionContent className="pb-5 text-max-text-secondary">
              <p>
                Не нашли нужный ответ? Напишите нам — мы постараемся помочь.
              </p>

              <a
                href="mailto:support@example.com"
                className="inline-block text-max-text-themed underline underline-offset-4"
              >
                support@example.com
              </a>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </section>
    </div>
  )
}
