import { ImageResponse } from "next/og";

import { getProblem, getTrack, problems } from "@/lib/content";
import { site } from "@/lib/site";

export const alt = "AI Engineer interview drill";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export function generateStaticParams() {
  return problems.map((problem) => ({ slug: problem.slug }));
}

/**
 * The share card. Dark, the title, the track accent, the difficulty, and the
 * one line that makes people click: it runs in the browser.
 *
 * Satori renders this, not a browser: every div needs an explicit display, and
 * fragments in the tree confuse it. Keep the markup flat.
 */
export default async function Image({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const problem = getProblem(slug);
  const track = problem ? getTrack(problem.track) : undefined;
  const accent = track?.accent ?? "#4F7CFF";

  const meta = [
    problem?.difficulty ?? "medium",
    `${problem?.timeBudgetMin ?? 25} min`,
    ...(problem?.companies?.length ? [problem.companies.slice(0, 3).join(", ")] : []),
  ].join("   ·   ");

  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          background: "#121417",
          color: "#E6E1D6",
          padding: 72,
          borderTop: `10px solid ${accent}`,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", fontSize: 26 }}>
          <div
            style={{
              width: 14,
              height: 14,
              borderRadius: 999,
              background: accent,
              marginRight: 16,
            }}
          />
          <div style={{ display: "flex", color: "#8C8A84", marginRight: 14 }}>
            {site.name}
          </div>
          <div style={{ display: "flex", color: "#343941", marginRight: 14 }}>/</div>
          <div style={{ display: "flex", color: accent }}>{track?.name ?? "drill"}</div>
        </div>

        <div style={{ display: "flex", flexDirection: "column" }}>
          <div
            style={{
              display: "flex",
              fontSize: 78,
              lineHeight: 1.05,
              letterSpacing: -1.5,
              marginBottom: 28,
            }}
          >
            {problem?.title ?? "AI engineering drills"}
          </div>
          <div style={{ display: "flex", fontSize: 26, color: "#8C8A84" }}>{meta}</div>
        </div>

        <div style={{ display: "flex", fontSize: 26, color: "#8C8A84" }}>
          Run it in your browser · no API key
        </div>
      </div>
    ),
    size,
  );
}
