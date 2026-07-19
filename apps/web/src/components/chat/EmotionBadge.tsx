import { cn } from "@/lib/utils/cn";

const toneFor = (emotion: string): string => {
  const key = emotion.toLowerCase();
  if (key.includes("anx") || key.includes("fear") || key.includes("worry")) {
    return "border-[rgba(140,170,220,0.4)] bg-[rgba(100,130,190,0.15)] text-[#c5d4f0]";
  }
  if (key.includes("anger") || key.includes("rage")) {
    return "border-[rgba(224,122,106,0.4)] bg-[rgba(224,122,106,0.12)] text-[#f0b4aa]";
  }
  if (key.includes("grief") || key.includes("sad") || key.includes("sorrow")) {
    return "border-[rgba(150,150,190,0.4)] bg-[rgba(120,120,160,0.14)] text-[#c8c8e0]";
  }
  if (key.includes("peace") || key.includes("calm") || key.includes("joy")) {
    return "border-[rgba(124,184,154,0.4)] bg-[rgba(124,184,154,0.12)] text-[#b8e0c8]";
  }
  return "border-[rgba(212,175,55,0.35)] bg-[rgba(212,175,55,0.1)] text-[var(--gold-soft)]";
};

export function EmotionBadge({ emotion }: { emotion: string }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs capitalize tracking-wide",
        toneFor(emotion),
      )}
    >
      {emotion}
    </span>
  );
}
