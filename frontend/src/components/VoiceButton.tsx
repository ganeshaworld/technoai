'use client';

import React, { useState, useEffect } from 'react';
import { Mic, MicOff, Volume2, VolumeX, Loader2 } from 'lucide-react';

interface VoiceButtonProps {
  onTranscription: (text: string) => void;
  lang?: string;
}

export default function VoiceButton({ onTranscription, lang = 'en-US' }: VoiceButtonProps) {
  const [isListening, setIsListening] = useState(false);
  const [isSupported, setIsSupported] = useState(true);
  const [recognition, setRecognition] = useState<any>(null);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const SpeechRecognition =
        (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

      if (SpeechRecognition) {
        const recog = new SpeechRecognition();
        recog.continuous = false;
        recog.interimResults = false;
        recog.lang = lang;

        recog.onresult = (event: any) => {
          const transcript = event.results[0][0].transcript;
          if (transcript) {
            onTranscription(transcript);
          }
          setIsListening(false);
        };

        recog.onerror = (e: any) => {
          console.warn('Speech recognition error:', e);
          setIsListening(false);
        };

        recog.onend = () => {
          setIsListening(false);
        };

        setRecognition(recog);
      } else {
        setIsSupported(false);
      }
    }
  }, [lang, onTranscription]);

  const toggleListening = () => {
    if (!recognition) return;
    if (isListening) {
      recognition.stop();
      setIsListening(false);
    } else {
      try {
        recognition.start();
        setIsListening(true);
      } catch (err) {
        console.warn('Failed to start speech recognition', err);
      }
    }
  };

  return (
    <button
      type="button"
      onClick={toggleListening}
      title={isListening ? 'Listening... click to stop' : 'Speak with Executive Assistant'}
      className={`relative flex items-center justify-center p-2.5 rounded-xl transition-all ${
        isListening
          ? 'bg-rose-500/20 text-rose-400 border border-rose-500/40 shadow-lg shadow-rose-500/20 animate-pulse'
          : 'bg-[#1E293B] text-slate-300 hover:text-white hover:bg-slate-700/80 border border-slate-700'
      }`}
    >
      {isListening ? (
        <>
          <span className="absolute -top-1 -right-1 flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-rose-500"></span>
          </span>
          <Mic className="w-4 h-4 text-rose-400 animate-bounce" />
        </>
      ) : (
        <Mic className="w-4 h-4" />
      )}
    </button>
  );
}
