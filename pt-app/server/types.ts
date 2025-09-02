// Individual work structure within the works_list
type WorkDetail = {
  work_id: string;
  display_name: string;
  publication_date: string; // ISO date string
  topic: string;
  fwci: number | null;
  cited_by_count: number;
  authorships: { display_name: string; author_position: number }[];
};

type Institution = {
  id: string;
  ror: string | null;
  display_name: string;
  ids: {
    openalex?: string | null;
    wikidata?: string | null;
    wikipedia?: string | null;
    grid?: string | null;
    ror?: string | null;
    mag?: string | null;
  };
  country_code: string | null;
  geo: {
    city: string | null;
    region: string | null;
    country: string | null;
    country_code: string | null;
    geonames_city_id: number | null;
    latitude: number | null;
    longitude: number | null;
  } | null;
  homepage_url: string | null;
  image_url: string | null;
  image_thumbnail_url: string | null;
};

// Main query result type with new fields for recency and productivity
export type AuthorRankingResult = {
  rank: string;
  id: string;
  display_name: string;
  ids: {
    openalex?: string | null;
    orcid?: string | null;
    scopus?: string | null;
    twitter?: string | null;
    wikipedia?: string | null;
  };
  summary_stats: {
    h_index: number | null;
    two_year_mean_citedness: number | null;
    i10_index: number | null;
  };
  latest_institution: Institution | null;
  works_list: WorkDetail[];
};
