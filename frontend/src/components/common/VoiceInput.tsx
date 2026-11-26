import { useCallback, useEffect, useRef } from "react"
import { Mic, Square } from "lucide-react"
import SpeechRecognition, {
  useSpeechRecognition,
} from "react-speech-recognition"
import { IconButton, useSnackbar } from "@maxhub/max-ui"

const errorMessages: Record<string, string> = {
  "not-allowed": "Разрешите доступ к микрофону в настройках браузера и обновите страницу.",
  "service-not-allowed": "Служба распознавания речи недоступна в браузере. Попробуйте позже.",
  "audio-capture": "Не удалось получить звук. Проверьте подключение и настройки микрофона.",
  network: "Не удалось связаться со службой распознавания. Проверьте интернет и попробуйте ещё раз.",
  "no-speech": "Речь не распознана. Попробуйте ещё раз и говорите ближе к микрофону.",
  "language-not-supported": "Распознавание русской речи недоступно в этом браузере.",
}

function abortRecognition() {
  const recognition = SpeechRecognition.getRecognition()
  // Запрещаем библиотеке автоматически перезапускаться после end.
  if (recognition) recognition.continuous = false
  void SpeechRecognition.abortListening().catch(() => {
    console.error("Ошибка голосового ввода:", "abort-failed")
  })
}

type VoiceInputProps = {
  onTranscript: (text: string) => void
  onListeningChange?: (listening: boolean) => void
}

export function VoiceInput({
  onTranscript,
  onListeningChange,
}: VoiceInputProps) {
  const { showSnackbar } = useSnackbar()
  const {
    transcript,
    listening,
    resetTranscript,
    browserSupportsSpeechRecognition,
    isMicrophoneAvailable,
  } = useSpeechRecognition()

  const onTranscriptRef = useRef(onTranscript)
  const onListeningChangeRef = useRef(onListeningChange)
  const showSnackbarRef = useRef(showSnackbar)
  const active = useRef(false)
  const receivedResult = useRef(false)
  const busy = useRef(false)

  useEffect(() => {
    onTranscriptRef.current = onTranscript
    onListeningChangeRef.current = onListeningChange
    showSnackbarRef.current = showSnackbar
  }, [onTranscript, onListeningChange, showSnackbar])

  const reportError = useCallback((code: string) => {
    console.error("Ошибка голосового ввода:", code)
    showSnackbarRef.current({
      text: "Не удалось распознать речь",
      caption: errorMessages[code] ?? "Не удалось выполнить голосовой ввод. Попробуйте ещё раз.",
      duration: 5000,
      placement: "top-center",
      offset: 16,
    })
  }, [])

  useEffect(() => {
    const recognition = SpeechRecognition.getRecognition()
    if (!recognition) return

    const handleError = (event: SpeechRecognitionErrorEvent) => {
      // abort после нажатия «Стоп» или ухода со страницы — штатная остановка.
      if (event.error === "aborted" && !active.current) return
      active.current = false
      busy.current = true
      reportError(event.error)
      abortRecognition()
    }
    const handleResult = (event: SpeechRecognitionEvent) => {
      receivedResult.current ||= Array.from(event.results).some(
        (result) => Boolean(result[0]?.transcript.trim())
      )
      // Текст по-прежнему передаётся через transcript библиотеки.
    }
    const handleEnd = () => {
      busy.current = false
      if (active.current && !receivedResult.current) {
        active.current = false
        abortRecognition()
        reportError("no-speech")
      }
    }

    // capture позволяет остановить распознавание до внутреннего обработчика библиотеки.
    recognition.addEventListener("error", handleError, true)
    recognition.addEventListener("result", handleResult)
    recognition.addEventListener("end", handleEnd, true)
    return () => {
      active.current = false
      recognition.removeEventListener("error", handleError, true)
      recognition.removeEventListener("result", handleResult)
      recognition.removeEventListener("end", handleEnd, true)
      abortRecognition()
    }
  }, [reportError])

  useEffect(() => {
    if (transcript) {
      onTranscriptRef.current(transcript)
    }
  }, [transcript])

  useEffect(() => {
    onListeningChangeRef.current?.(listening)
  }, [listening])

  const toggleListening = async () => {
    if (busy.current) return
    busy.current = true
    if (listening) {
      active.current = false
      const recognition = SpeechRecognition.getRecognition()
      if (recognition) recognition.continuous = false
      void SpeechRecognition.stopListening().catch(() => {
        busy.current = false
        reportError("stop-failed")
        abortRecognition()
      })
      return
    }

    resetTranscript()
    active.current = true
    receivedResult.current = false

    try {
      await SpeechRecognition.startListening({
        language: "ru-RU",
        continuous: true,
      })
      if (active.current) busy.current = false
    } catch {
      active.current = false
      busy.current = false
      reportError("start-failed")
      abortRecognition()
    }
  }

  if (!browserSupportsSpeechRecognition) {
    return null
  }

  return (
    <IconButton
      variant={listening ? "primary" : "secondary"}
      type="button"
      onClick={toggleListening}
      disabled={!isMicrophoneAvailable}
      aria-label={
        listening ? "Завершить голосовой ввод" : "Начать голосовой ввод"
      }
      aria-pressed={listening}
      size="small"
    >
      {listening ? <Square className="size-5" /> : <Mic className="size-5" />}
    </IconButton>
  )
}
