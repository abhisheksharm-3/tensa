"use client";

import type { FieldProps, OptionsPanelProps } from "@/components/types";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  AUDIO_BITRATES,
  AUDIO_FORMATS,
  TRANSCRIPT_FORMATS,
  VIDEO_FORMATS,
  WHISPER_MODELS,
} from "@/constants/options";
import type {
  AudioBitrate,
  AudioFormat,
  TranscriptFormat,
  VideoFormat,
  WhisperModel,
} from "@/types/job";

function Field({ label, children }: FieldProps) {
  return (
    <div className="flex flex-col gap-1">
      <Label className="text-xs text-muted-foreground">{label}</Label>
      {children}
    </div>
  );
}

export function OptionsPanel({ mode, values, onChange }: OptionsPanelProps) {
  if (mode === "download" || mode === "playlist") return null;

  return (
    <div className="flex flex-wrap items-end gap-3">
      {mode === "audio" && (
        <>
          <Field label="Format">
            <Select
              value={values.audioFormat}
              onValueChange={(v) => onChange({ audioFormat: v as AudioFormat })}
            >
              <SelectTrigger size="sm" className="w-28 text-xs">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {AUDIO_FORMATS.map((format) => (
                  <SelectItem key={format} value={format} className="text-xs">
                    {format.toUpperCase()}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </Field>
          <Field label="Bitrate">
            <Select
              value={values.audioBitrate}
              onValueChange={(v) =>
                onChange({ audioBitrate: v as AudioBitrate })
              }
            >
              <SelectTrigger size="sm" className="w-28 text-xs">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {AUDIO_BITRATES.map((bitrate) => (
                  <SelectItem key={bitrate} value={bitrate} className="text-xs">
                    {bitrate}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </Field>
        </>
      )}

      {mode === "convert" && (
        <Field label="Output format">
          <Select
            value={values.videoFormat}
            onValueChange={(v) => onChange({ videoFormat: v as VideoFormat })}
          >
            <SelectTrigger size="sm" className="w-28 text-xs">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {VIDEO_FORMATS.map((format) => (
                <SelectItem key={format} value={format} className="text-xs">
                  {format.toUpperCase()}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </Field>
      )}

      {mode === "transcribe" && (
        <>
          <Field label="Model">
            <Select
              value={values.whisperModel}
              onValueChange={(v) =>
                onChange({ whisperModel: v as WhisperModel })
              }
            >
              <SelectTrigger size="sm" className="w-28 text-xs">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {WHISPER_MODELS.map((model) => (
                  <SelectItem
                    key={model}
                    value={model}
                    className="text-xs capitalize"
                  >
                    {model}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </Field>
          <Field label="Output">
            <Select
              value={values.transcriptFormat}
              onValueChange={(v) =>
                onChange({ transcriptFormat: v as TranscriptFormat })
              }
            >
              <SelectTrigger size="sm" className="w-24 text-xs">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {TRANSCRIPT_FORMATS.map((format) => (
                  <SelectItem key={format} value={format} className="text-xs">
                    {format.toUpperCase()}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </Field>
        </>
      )}
    </div>
  );
}
