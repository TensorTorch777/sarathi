/** PCM helpers and interruptible playback queue for voice mode. */

export function floatTo16BitPCM(float32: Float32Array): ArrayBuffer {
  const buffer = new ArrayBuffer(float32.length * 2);
  const view = new DataView(buffer);
  for (let i = 0; i < float32.length; i += 1) {
    const s = Math.max(-1, Math.min(1, float32[i] ?? 0));
    view.setInt16(i * 2, s < 0 ? s * 0x8000 : s * 0x7fff, true);
  }
  return buffer;
}

export function mergeFloat32(chunks: Float32Array[]): Float32Array {
  const total = chunks.reduce((sum, c) => sum + c.length, 0);
  const out = new Float32Array(total);
  let offset = 0;
  for (const chunk of chunks) {
    out.set(chunk, offset);
    offset += chunk.length;
  }
  return out;
}

export function arrayBufferToBase64(buffer: ArrayBuffer): string {
  const bytes = new Uint8Array(buffer);
  let binary = "";
  const chunk = 0x8000;
  for (let i = 0; i < bytes.length; i += chunk) {
    binary += String.fromCharCode(...bytes.subarray(i, i + chunk));
  }
  return btoa(binary);
}

export function base64ToArrayBuffer(b64: string): ArrayBuffer {
  const binary = atob(b64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes.buffer;
}

export class PcmPlaybackQueue {
  private readonly ctx: AudioContext;
  private queue: AudioBufferSourceNode[] = [];
  private playing = false;
  private nextTime = 0;
  private onIdle: (() => void) | null = null;

  constructor(sampleRate = 22050) {
    this.ctx = new AudioContext({ sampleRate });
  }

  get context(): AudioContext {
    return this.ctx;
  }

  setIdleHandler(handler: (() => void) | null): void {
    this.onIdle = handler;
  }

  async resume(): Promise<void> {
    if (this.ctx.state === "suspended") {
      await this.ctx.resume();
    }
  }

  enqueuePcm16(pcm: ArrayBuffer, sampleRate: number): void {
    const int16 = new Int16Array(pcm);
    const float32 = new Float32Array(int16.length);
    for (let i = 0; i < int16.length; i += 1) {
      float32[i] = (int16[i] ?? 0) / 32768;
    }
    const buffer = this.ctx.createBuffer(1, float32.length, sampleRate);
    buffer.copyToChannel(float32, 0);

    const source = this.ctx.createBufferSource();
    source.buffer = buffer;
    source.connect(this.ctx.destination);

    const startAt = Math.max(this.ctx.currentTime, this.nextTime);
    source.start(startAt);
    this.nextTime = startAt + buffer.duration;
    this.playing = true;
    this.queue.push(source);

    source.onended = () => {
      this.queue = this.queue.filter((node) => node !== source);
      if (this.queue.length === 0) {
        this.playing = false;
        this.onIdle?.();
      }
    };
  }

  /** Hard stop for barge-in / interrupt. */
  interrupt(): void {
    for (const source of this.queue) {
      try {
        source.stop();
        source.disconnect();
      } catch {
        // already stopped
      }
    }
    this.queue = [];
    this.playing = false;
    this.nextTime = this.ctx.currentTime;
  }

  get isPlaying(): boolean {
    return this.playing;
  }

  async close(): Promise<void> {
    this.interrupt();
    await this.ctx.close();
  }
}
