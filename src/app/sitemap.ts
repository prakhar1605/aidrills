import type { MetadataRoute } from "next";

import { problems, tracks } from "@/lib/content";
import { site } from "@/lib/site";

export default function sitemap(): MetadataRoute.Sitemap {
  const staticRoutes = ["", "/problems", "/roadmap", "/resources", "/contribute"].map(
    (path) => ({
      url: `${site.url}${path}`,
      changeFrequency: "weekly" as const,
      priority: path === "" ? 1 : 0.7,
    }),
  );

  return [
    ...staticRoutes,
    ...tracks.map((track) => ({
      url: `${site.url}/tracks/${track.id}`,
      changeFrequency: "weekly" as const,
      priority: 0.6,
    })),
    ...problems.map((problem) => ({
      url: `${site.url}/problems/${problem.slug}`,
      changeFrequency: "monthly" as const,
      priority: 0.8,
    })),
  ];
}
