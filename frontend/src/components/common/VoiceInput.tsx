import { useEffect, useRef } from "react"
import { Mic, Square } from "lucide-react"
import SpeechRecognition, {
  useSpeechRecognition,
} from "react-speech-recognition"
import { IconButton } from "@maxhub/max-ui"

type VoiceInputProps = {
  onTranscript: (text: string) => void
  onListeningChange?: (listening: boolean) => void
}

export function VoiceInput({
  onTranscript,
  onListeningChange,
}: VoiceInputProps) {
  const {
    transcript,
    listening,
    resetTranscript,
    browserSupportsSpeechRecognition,
    isMicrophoneAvailable,
  } = useSpeechRecognition()

  const onTranscriptRef = useRef(onTranscript)
  const onListeningChangeRef = useRef(onListeningChange)

  useEffect(() => {
    onTranscriptRef.current = onTranscript
    onListeningChangeRef.current = onListeningChange
  }, [onTranscript, onListeningChange])

  useEffect(() => {
    if (transcript) {
      onTranscriptRef.current(transcript)
    }
  }, [transcript])

  useEffect(() => {
    onListeningChangeRef.current?.(listening)
  }, [listening])

  const toggleListening = async () => {
    if (listening) {
      await SpeechRecognition.stopListening()
      return
    }

    resetTranscript()

    try {
      await SpeechRecognition.startListening({
        language: "ru-RU",
        continuous: true,
      })
    } catch {
      // setError("Не удалось включить микрофон")
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
