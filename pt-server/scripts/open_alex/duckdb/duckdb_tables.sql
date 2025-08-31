-- DuckDB table definitions for OpenAlex entities

-- Works table
DROP TABLE works;
CREATE TABLE IF NOT EXISTS works (
    -- Basic identifiers
    id VARCHAR PRIMARY KEY,
    doi VARCHAR,
    title VARCHAR,
    display_name VARCHAR,
    -- publication_year INTEGER,
    publication_date DATE,
    language VARCHAR,
    type VARCHAR,
    oa_url VARCHAR, -- new
    -- type_crossref VARCHAR,
    
    -- IDs object
    ids STRUCT(
        openalex VARCHAR,
        doi VARCHAR,
        mag BIGINT,
        pmid VARCHAR,
        pmcid VARCHAR
    ),

    primary_topic_id VARCHAR, -- new, to link to topics table
    citation_normalized_percentile_value DOUBLE, -- new, to store percentile directly
    

    -- authorships STRUCT(
    --     id VARCHAR,
    --     display_name VARCHAR,
    --     orcid VARCHAR
    -- )[],
    
    -- Citation metrics
    cited_by_count INTEGER,
    fwci DOUBLE,
    
    -- -- Citation normalized percentile
    -- citation_normalized_percentile STRUCT(
    --     value DOUBLE,
    --     is_in_top_1_percent BOOLEAN,
    --     is_in_top_10_percent BOOLEAN
    -- ),
    
    -- Bibliography
    -- biblio STRUCT(
    --     volume VARCHAR,
    --     issue VARCHAR,
    --     first_page VARCHAR,
    --     last_page VARCHAR
    -- ),
    
    -- Open Access
    -- open_access STRUCT(
    --     is_oa BOOLEAN,
    --     oa_status VARCHAR, -- gold, green, hybrid, bronze, closed, diamond
    --     oa_url VARCHAR,
    --     any_repository_has_fulltext BOOLEAN
    -- ),
    
    -- Primary location
    -- primary_location STRUCT(
    --     is_oa BOOLEAN,
    --     landing_page_url VARCHAR,
    --     pdf_url VARCHAR,
    --     license VARCHAR,
    --     license_id VARCHAR,
    --     version VARCHAR, -- publishedVersion, acceptedVersion, submittedVersion
    --     is_accepted BOOLEAN,
    --     is_published BOOLEAN,
    --     source STRUCT(
    --         id VARCHAR,
    --         display_name VARCHAR,
    --         issn_l VARCHAR,
    --         issn VARCHAR[],
    --         is_oa BOOLEAN,
    --         is_in_doaj BOOLEAN,
    --         is_indexed_in_scopus BOOLEAN,
    --         is_core BOOLEAN,
    --         host_organization VARCHAR,
    --         host_organization_name VARCHAR,
    --         host_organization_lineage VARCHAR[],
    --         host_organization_lineage_names VARCHAR[],
    --         type VARCHAR -- journal, repository, conference
    --     )
    -- ),
    
    -- Best OA location (same schema as primary_location)
    -- best_oa_location STRUCT(
    --     is_oa BOOLEAN,
    --     landing_page_url VARCHAR,
    --     pdf_url VARCHAR,
    --     license VARCHAR,
    --     license_id VARCHAR,
    --     version VARCHAR,
    --     is_accepted BOOLEAN,
    --     is_published BOOLEAN,
    --     source STRUCT(
    --         id VARCHAR,
    --         display_name VARCHAR,
    --         issn_l VARCHAR,
    --         issn VARCHAR[],
    --         is_oa BOOLEAN,
    --         is_in_doaj BOOLEAN,
    --         is_indexed_in_scopus BOOLEAN,
    --         is_core BOOLEAN,
    --         host_organization VARCHAR,
    --         host_organization_name VARCHAR,
    --         host_organization_lineage VARCHAR[],
    --         host_organization_lineage_names VARCHAR[],
    --         type VARCHAR
    --     )
    -- ),
    
    -- Locations (list of structs) - OPTIONAL
    -- locations STRUCT(
    --     is_oa BOOLEAN,
    --     landing_page_url VARCHAR,
    --     pdf_url VARCHAR,
    --     license VARCHAR,
    --     license_id VARCHAR,
    --     version VARCHAR,
    --     is_accepted BOOLEAN,
    --     is_published BOOLEAN,
    --     source STRUCT(
    --         id VARCHAR,
    --         display_name VARCHAR,
    --         issn_l VARCHAR,
    --         issn VARCHAR[],
    --         is_oa BOOLEAN,
    --         is_in_doaj BOOLEAN,
    --         is_indexed_in_scopus BOOLEAN,
    --         is_core BOOLEAN,
    --         host_organization VARCHAR,
    --         host_organization_name VARCHAR,
    --         host_organization_lineage VARCHAR[],
    --         host_organization_lineage_names VARCHAR[],
    --         type VARCHAR
    --     )
    -- )[],
    -- locations_count INTEGER,
    
    -- Authorships (list of structs) - OPTIONAL
    -- authorships STRUCT(
    --     author_position VARCHAR, -- first, middle, last
    --     is_corresponding BOOLEAN,
    --     raw_author_name VARCHAR,
    --     raw_affiliation_strings VARCHAR[],
    --     author STRUCT(
    --         id VARCHAR,
    --         display_name VARCHAR,
    --         orcid VARCHAR
    --     ),
    --     institutions STRUCT(
    --         id VARCHAR,
    --         display_name VARCHAR,
    --         ror VARCHAR,
    --         country_code VARCHAR,
    --         type VARCHAR,
    --         lineage VARCHAR[]
    --     )[],
    --     countries VARCHAR[],
    --     affiliations STRUCT(
    --         raw_affiliation_string VARCHAR,
    --         institution_ids VARCHAR[]
    --     )[]
    -- )[],
    
    -- Authorship counters
    -- corresponding_author_ids VARCHAR[],
    -- corresponding_institution_ids VARCHAR[],
    -- countries_distinct_count INTEGER,
    -- institutions_distinct_count INTEGER,
    
    -- Topics (list of structs) - OPTIONAL
    -- topics STRUCT(
    --     id VARCHAR,
    --     display_name VARCHAR,
    --     score DOUBLE,
    --     subfield STRUCT(id VARCHAR, display_name VARCHAR),
    --     field STRUCT(id VARCHAR, display_name VARCHAR),
    --     domain STRUCT(id VARCHAR, display_name VARCHAR)
    -- )[],
    
    -- Primary topic
    -- primary_topic STRUCT(
    --     id VARCHAR,
    --     display_name VARCHAR,
    --     score DOUBLE,
    --     subfield STRUCT(id VARCHAR, display_name VARCHAR),
    --     field STRUCT(id VARCHAR, display_name VARCHAR),
    --     domain STRUCT(id VARCHAR, display_name VARCHAR)
    -- ),
    
    -- Keywords (list of structs) - OPTIONAL
    -- keywords STRUCT(
    --     id VARCHAR,
    --     display_name VARCHAR,
    --     score DOUBLE
    -- )[],
    
    -- Concepts (deprecated but still present) - OPTIONAL
    -- concepts STRUCT(
    --     id VARCHAR,
    --     wikidata VARCHAR,
    --     display_name VARCHAR,
    --     level INTEGER,
    --     score DOUBLE
    -- )[],
    
    -- Sustainable Development Goals - OPTIONAL
    -- sustainable_development_goals STRUCT(
    --     id VARCHAR,
    --     display_name VARCHAR,
    --     score DOUBLE
    -- )[],
    
    -- MeSH tags - OPTIONAL
    -- mesh STRUCT(
    --     descriptor_ui VARCHAR,
    --     descriptor_name VARCHAR,
    --     qualifier_ui VARCHAR,
    --     qualifier_name VARCHAR,
    --     is_major_topic BOOLEAN
    -- )[],
    
    -- APC (Article Processing Charges)
    -- apc_list STRUCT(
    --     value INTEGER,
    --     currency VARCHAR,
    --     value_usd INTEGER,
    --     provenance VARCHAR
    -- ),
    -- apc_paid STRUCT(
    --     value INTEGER,
    --     currency VARCHAR,
    --     value_usd INTEGER,
    --     provenance VARCHAR
    -- ),
    
    -- Grants - OPTIONAL
    -- grants STRUCT(
    --     funder VARCHAR,
    --     funder_display_name VARCHAR,
    --     award_id VARCHAR
    -- )[],
    
    -- References and related works - OPTIONAL
    -- referenced_works VARCHAR[],
    -- referenced_works_count INTEGER,
    -- related_works VARCHAR[],
    
    -- Abstract inverted index (stored as JSON string)
    -- abstract_inverted_index VARCHAR, -- JSON string
    
    -- Counts by year - OPTIONAL
    -- counts_by_year STRUCT(
    --     year INTEGER,
    --     cited_by_count INTEGER
    -- )[],
    
    -- Boolean flags
    -- has_fulltext BOOLEAN,
    -- fulltext_origin VARCHAR, -- pdf, ngrams
    -- is_retracted BOOLEAN,
    -- is_paratext BOOLEAN,
    
    -- Indexed in - OPTIONAL
    -- indexed_in VARCHAR[], -- crossref, doaj, pubmed, arxiv
    
    -- Datasets and versions - OPTIONAL
    -- datasets VARCHAR[],
    -- versions VARCHAR[],
    
    -- Institution assertions (stored as JSON string)
    -- institution_assertions VARCHAR, -- JSON string
    
    -- Citation percentile by year
    -- cited_by_percentile_year STRUCT(
    --     min INTEGER,
    --     max INTEGER
    -- ),
    
    -- Timestamps
    created_date DATE,
    updated_date TIMESTAMPTZ
);

-- API Queries table - tracks search queries used to search OpenAlex works
-- DROP TABLE works_api_queries;
-- DROP TABLE api_queries;
CREATE TABLE IF NOT EXISTS api_queries (
    query_text VARCHAR PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    max_pages INTEGER,
    total_results INTEGER
);

-- Works API Queries table - N:M relationship between queries and works
CREATE TABLE IF NOT EXISTS works_api_queries (
    query_text VARCHAR NOT NULL,
    work_id VARCHAR NOT NULL,
    page_number INTEGER NOT NULL,
    position_in_page INTEGER,
    relevance_score DOUBLE NOT NULL,    
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (query_text, work_id),
);
-- Authors table
-- DROP TABLE IF EXISTS author_topics;
-- DROP TABLE IF EXISTS author_affiliations;
-- DROP TABLE IF EXISTS authors;
CREATE TABLE IF NOT EXISTS authors (
    -- Basic identifiers
    id VARCHAR PRIMARY KEY,
    orcid VARCHAR,
    display_name VARCHAR,
    display_name_alternatives VARCHAR[],
    
    -- Production metrics
    works_count INTEGER,
    cited_by_count INTEGER,
    
    -- Summary statistics
    summary_stats STRUCT(
        "2yr_mean_citedness" DOUBLE,
        h_index INTEGER,
        i10_index INTEGER
    ),
    
    -- External IDs
    ids STRUCT(
        openalex VARCHAR,
        orcid VARCHAR,
        scopus VARCHAR,
        twitter VARCHAR,
        wikipedia VARCHAR
    ),
    
    -- Affiliations -- commented out to optimize state, will be in different table
    -- affiliations STRUCT(
    --     institution STRUCT(
    --         id VARCHAR,
    --         ror VARCHAR,
    --         display_name VARCHAR,
    --         country_code VARCHAR,
    --         type VARCHAR,
    --         lineage VARCHAR[]
    --     ),
    --     years INTEGER[]
    -- )[],
    
    -- Last known institutions -- commented out to optimize space
    -- last_known_institutions STRUCT(
    --     id VARCHAR,
    --     ror VARCHAR,
    --     display_name VARCHAR,
    --     country_code VARCHAR,
    --     type VARCHAR,
    --     lineage VARCHAR[]
    -- )[],
    
    -- Topics -- commented out to optimize space
    -- topics STRUCT(
    --     id VARCHAR,
    --     display_name VARCHAR,
    --     count INTEGER,
    --     subfield STRUCT(id VARCHAR, display_name VARCHAR),
    --     field STRUCT(id VARCHAR, display_name VARCHAR),
    --     domain STRUCT(id VARCHAR, display_name VARCHAR)
    -- )[],
    
    -- Topic share -- commented out to optimize space, will be in different table
    -- topic_share STRUCT(
    --     id VARCHAR,
    --     display_name VARCHAR,
    --     value DOUBLE,
    --     subfield STRUCT(id VARCHAR, display_name VARCHAR),
    --     field STRUCT(id VARCHAR, display_name VARCHAR),
    --     domain STRUCT(id VARCHAR, display_name VARCHAR)
    -- )[],
    
    -- X concepts (deprecated) -- commented out to optimize space
    --     id VARCHAR,
    --     wikidata VARCHAR,
    --     display_name VARCHAR,
    --     level INTEGER,
    --     score DOUBLE
    -- )[],
    
    -- Counts by year -- commented out to optimize space
    -- counts_by_year STRUCT(
    --     year INTEGER,
    --     works_count INTEGER,
    --     cited_by_count INTEGER
    -- )[],
    
    -- API URLs -- commented out to optimize space
    -- works_api_url VARCHAR,
    
    -- Timestamps -- commented out to optimize space
    -- created_date DATE,
    -- updated_date TIMESTAMPTZ
);

-- Subfields table
CREATE TABLE IF NOT EXISTS subfields (
    -- Basic identifiers
    id VARCHAR PRIMARY KEY,
    display_name VARCHAR,
    description VARCHAR,
    display_name_alternatives VARCHAR[],
    
    -- External IDs
    ids STRUCT(
        wikidata VARCHAR,
        wikipedia VARCHAR
    ),
    
    -- Academic hierarchy
    field STRUCT(
        id VARCHAR,
        display_name VARCHAR
    ),
    domain STRUCT(
        id VARCHAR,
        display_name VARCHAR
    ),
    
    -- Topics
    topics STRUCT(
        id VARCHAR,
        display_name VARCHAR
    )[],
    
    -- Siblings
    siblings STRUCT(
        id VARCHAR,
        display_name VARCHAR
    )[],
    
    -- Metrics
    works_count BIGINT,
    cited_by_count BIGINT,
    
    -- API URLs
    works_api_url VARCHAR,
    
    -- Timestamps (as strings per actual data)
    updated_date VARCHAR,
    created_date VARCHAR,
    updated VARCHAR
);

-- Publishers table
CREATE TABLE IF NOT EXISTS publishers (
    -- Basic identifiers
    id VARCHAR PRIMARY KEY,
    display_name VARCHAR,
    
    -- External IDs
    ids STRUCT(
        openalex VARCHAR,
        wikidata VARCHAR,
        ror VARCHAR
    ),
    
    -- Titles and hierarchy
    alternate_titles VARCHAR[],
    parent_publisher VARCHAR,
    lineage VARCHAR[],
    hierarchy_level BIGINT,
    
    -- Location and URLs
    country_codes VARCHAR[],
    homepage_url VARCHAR,
    image_url VARCHAR,
    image_thumbnail_url VARCHAR,
    
    -- Roles
    roles STRUCT(
        role VARCHAR,
        id VARCHAR,
        works_count BIGINT
    )[],
    
    -- Basic metrics
    works_count BIGINT,
    cited_by_count BIGINT,
    sources_count BIGINT,
    
    -- Summary statistics
    summary_stats STRUCT(
        "2yr_mean_citedness" DOUBLE,
        h_index BIGINT,
        i10_index BIGINT
    ),
    
    -- Counts by year
    counts_by_year STRUCT(
        year BIGINT,
        works_count BIGINT,
        oa_works_count BIGINT,
        cited_by_count BIGINT
    )[],
    
    -- X concepts (deprecated)
    x_concepts STRUCT(
        id VARCHAR,
        wikidata VARCHAR,
        display_name VARCHAR,
        level BIGINT,
        score DOUBLE
    )[],
    
    -- API URLs
    sources_api_url VARCHAR,
    
    -- Timestamps
    updated_date VARCHAR,
    created_date VARCHAR,
    updated VARCHAR
);

-- Sources table
CREATE TABLE IF NOT EXISTS sources (
    -- Basic identifiers
    id VARCHAR PRIMARY KEY,
    display_name VARCHAR,
    abbreviated_title VARCHAR,
    
    -- External IDs
    ids STRUCT(
        openalex VARCHAR,
        issn_l VARCHAR,
        issn VARCHAR[],
        mag BIGINT,
        fatcat VARCHAR,
        wikidata VARCHAR
    ),
    
    -- ISSN information
    issn_l VARCHAR,
    issn VARCHAR[],
    
    -- Alternative titles
    alternate_titles VARCHAR[],
    
    -- Host organization
    host_organization VARCHAR,
    host_organization_name VARCHAR,
    host_organization_lineage VARCHAR[],
    
    -- Location and URLs
    country_code VARCHAR,
    homepage_url VARCHAR,
    
    -- Type and flags
    type VARCHAR,
    is_oa BOOLEAN,
    is_in_doaj BOOLEAN,
    is_core BOOLEAN,
    
    -- Article Processing Charges
    apc_prices STRUCT(
        price INTEGER,
        currency VARCHAR
    )[],
    apc_usd INTEGER,
    
    -- Societies
    societies STRUCT(
        url VARCHAR,
        organization VARCHAR
    )[],
    
    -- Summary statistics
    summary_stats STRUCT(
        "2yr_mean_citedness" DOUBLE,
        h_index INTEGER,
        i10_index INTEGER
    ),
    
    -- Basic metrics
    works_count INTEGER,
    cited_by_count INTEGER,
    
    -- Counts by year
    counts_by_year STRUCT(
        year INTEGER,
        works_count INTEGER,
        cited_by_count INTEGER
    )[],
    
    -- X concepts (deprecated)
    x_concepts STRUCT(
        id VARCHAR,
        wikidata VARCHAR,
        display_name VARCHAR,
        level INTEGER,
        score DOUBLE
    )[],
    
    -- API URLs
    works_api_url VARCHAR,
    
    -- Timestamps
    created_date VARCHAR,
    updated_date VARCHAR
);

-- Funders table
CREATE TABLE IF NOT EXISTS funders (
    -- Basic identifiers
    id VARCHAR PRIMARY KEY,
    display_name VARCHAR,
    description VARCHAR,
    
    -- Alternative titles
    alternate_titles VARCHAR[],
    
    -- External IDs
    ids STRUCT(
        openalex VARCHAR,
        ror VARCHAR,
        wikidata VARCHAR,
        crossref VARCHAR,
        doi VARCHAR
    ),
    
    -- Location and URLs
    country_code VARCHAR,
    homepage_url VARCHAR,
    image_url VARCHAR,
    image_thumbnail_url VARCHAR,
    
    -- Basic counters
    works_count INTEGER,
    cited_by_count INTEGER,
    grants_count INTEGER,
    
    -- Summary statistics
    summary_stats STRUCT(
        "2yr_mean_citedness" DOUBLE,
        h_index INTEGER,
        i10_index INTEGER
    ),
    
    -- Roles
    roles STRUCT(
        role VARCHAR,
        id VARCHAR,
        works_count INTEGER
    )[],
    
    -- Counts by year
    counts_by_year STRUCT(
        year INTEGER,
        works_count INTEGER,
        cited_by_count INTEGER
    )[],
    
    -- Timestamps
    created_date VARCHAR,
    updated_date VARCHAR
);

-- Institutions table
CREATE TABLE IF NOT EXISTS institutions (
    -- Basic identifiers
    id VARCHAR PRIMARY KEY,
    ror VARCHAR,
    display_name VARCHAR,
    display_name_acronyms VARCHAR[],
    display_name_alternatives VARCHAR[],
    
    -- External IDs
    ids STRUCT(
        openalex VARCHAR,
        ror VARCHAR,
        grid VARCHAR,
        wikipedia VARCHAR,
        wikidata VARCHAR,
        mag BIGINT
    ),
    
    -- Location and geography
    country_code VARCHAR,
    geo STRUCT(
        city VARCHAR,
        geonames_city_id VARCHAR,
        region VARCHAR,
        country_code VARCHAR,
        country VARCHAR,
        latitude DOUBLE,
        longitude DOUBLE
    ),
    
    -- URLs and images
    homepage_url VARCHAR,
    image_url VARCHAR,
    image_thumbnail_url VARCHAR,
    
    -- Type and flags
    type VARCHAR,
    is_super_system BOOLEAN,
    
    -- Basic counters
    works_count INTEGER,
    cited_by_count INTEGER,
    
    -- Summary statistics
    summary_stats STRUCT(
        "2yr_mean_citedness" DOUBLE,
        h_index INTEGER,
        i10_index INTEGER
    ),
    
    -- Hierarchy and relationships
    lineage VARCHAR[],
    associated_institutions STRUCT(
        id VARCHAR,
        ror VARCHAR,
        display_name VARCHAR,
        country_code VARCHAR,
        type VARCHAR,
        relationship VARCHAR
    )[],
    
    -- Roles
    roles STRUCT(
        role VARCHAR,
        id VARCHAR,
        works_count INTEGER
    )[],
    
    -- Repositories
    repositories STRUCT(
        id VARCHAR,
        display_name VARCHAR,
        host_organization VARCHAR,
        host_organization_name VARCHAR,
        host_organization_lineage VARCHAR[]
    )[],
    
    -- International names
    international STRUCT(
        display_name VARCHAR -- JSON string representing language code -> name dict
    ),
    
    -- Counts by year
    counts_by_year STRUCT(
        year INTEGER,
        works_count INTEGER,
        cited_by_count INTEGER
    )[],
    
    -- X concepts (deprecated)
    x_concepts STRUCT(
        id VARCHAR,
        wikidata VARCHAR,
        display_name VARCHAR,
        level INTEGER,
        score DOUBLE
    )[],
    
    -- API URLs
    works_api_url VARCHAR,
    
    -- Timestamps
    created_date VARCHAR,
    updated_date VARCHAR
);

-- Concepts table (deprecated but still present in data)
CREATE TABLE IF NOT EXISTS concepts (
    -- Basic identifiers
    id VARCHAR PRIMARY KEY,
    wikidata VARCHAR,
    display_name VARCHAR,
    level BIGINT,
    description VARCHAR,
    
    -- Metrics
    works_count BIGINT,
    cited_by_count BIGINT,
    
    -- Summary statistics (extended)
    summary_stats STRUCT(
        "2yr_mean_citedness" DOUBLE,
        h_index BIGINT,
        i10_index BIGINT,
        oa_percent DOUBLE,
        works_count BIGINT,
        cited_by_count BIGINT,
        "2yr_works_count" BIGINT,
        "2yr_cited_by_count" BIGINT,
        "2yr_i10_index" BIGINT,
        "2yr_h_index" BIGINT
    ),
    
    -- External IDs
    ids STRUCT(
        openalex VARCHAR,
        wikidata VARCHAR,
        wikipedia VARCHAR,
        umls_aui VARCHAR[],
        umls_cui VARCHAR[],
        mag BIGINT
    ),
    
    -- Images
    image_url VARCHAR,
    image_thumbnail_url VARCHAR,
    
    -- International names and descriptions (simplified as JSON strings due to complexity)
    international STRUCT(
        display_name VARCHAR, -- JSON string with language codes
        description VARCHAR   -- JSON string with language codes
    ),
    
    -- Relationships
    ancestors STRUCT(
        id VARCHAR,
        wikidata VARCHAR,
        display_name VARCHAR,
        level BIGINT
    )[],
    related_concepts STRUCT(
        id VARCHAR,
        wikidata VARCHAR,
        display_name VARCHAR,
        level BIGINT,
        score DOUBLE
    )[],
    
    -- Counts by year
    counts_by_year STRUCT(
        year BIGINT,
        works_count BIGINT,
        oa_works_count BIGINT,
        cited_by_count BIGINT
    )[],
    
    -- API URLs
    works_api_url VARCHAR,
    
    -- Timestamps
    updated_date VARCHAR,
    created_date VARCHAR,
    updated VARCHAR
);

-- Domains table
CREATE TABLE IF NOT EXISTS domains (
    -- Basic identifiers
    id VARCHAR PRIMARY KEY,
    display_name VARCHAR,
    description VARCHAR,
    display_name_alternatives VARCHAR[],
    
    -- External IDs
    ids STRUCT(
        wikidata VARCHAR,
        wikipedia VARCHAR
    ),
    
    -- Relationships
    fields STRUCT(
        id VARCHAR,
        display_name VARCHAR
    )[],
    siblings STRUCT(
        id VARCHAR,
        display_name VARCHAR
    )[],
    
    -- Metrics
    works_count BIGINT,
    cited_by_count BIGINT,
    
    -- API URLs
    works_api_url VARCHAR,
    
    -- Timestamps
    updated_date VARCHAR,
    created_date VARCHAR,
    updated VARCHAR
);

-- Fields table
CREATE TABLE IF NOT EXISTS fields (
    -- Basic identifiers
    id VARCHAR PRIMARY KEY,
    display_name VARCHAR,
    description VARCHAR,
    display_name_alternatives VARCHAR[],
    
    -- External IDs
    ids STRUCT(
        wikidata VARCHAR,
        wikipedia VARCHAR
    ),
    
    -- Academic hierarchy
    domain STRUCT(
        id VARCHAR,
        display_name VARCHAR
    ),
    
    -- Relationships
    subfields STRUCT(
        id VARCHAR,
        display_name VARCHAR
    )[],
    siblings STRUCT(
        id VARCHAR,
        display_name VARCHAR
    )[],
    
    -- Metrics
    works_count BIGINT,
    cited_by_count BIGINT,
    
    -- API URLs
    works_api_url VARCHAR,
    
    -- Timestamps
    updated_date VARCHAR,
    created_date VARCHAR,
    updated VARCHAR
);

-- Topics table
CREATE TABLE IF NOT EXISTS topics (
    -- Basic identifiers
    id VARCHAR PRIMARY KEY,
    display_name VARCHAR,
    
    -- Academic hierarchy
    subfield STRUCT(
        id VARCHAR,
        display_name VARCHAR
    ),
    field STRUCT(
        id VARCHAR,
        display_name VARCHAR
    ),
    domain STRUCT(
        id VARCHAR,
        display_name VARCHAR
    ),
    
    -- Description and keywords
    description VARCHAR,
    keywords VARCHAR[],
    
    -- External IDs
    ids STRUCT(
        openalex VARCHAR,
        wikipedia VARCHAR
    ),
    
    -- Siblings
    siblings STRUCT(
        id VARCHAR,
        display_name VARCHAR
    )[],
    
    -- Metrics
    works_count BIGINT,
    cited_by_count BIGINT,
    
    -- API URLs
    works_api_url VARCHAR,
    
    -- Timestamps
    updated_date VARCHAR,
    created_date VARCHAR,
    updated VARCHAR
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_works_display_name ON works(display_name);
-- CREATE INDEX IF NOT EXISTS idx_works_publication_year ON works(publication_year);
-- CREATE INDEX IF NOT EXISTS idx_works_cited_by_count ON works(cited_by_count);
CREATE INDEX IF NOT EXISTS idx_works_type ON works(type);
CREATE INDEX IF NOT EXISTS idx_works_language ON works(language);
CREATE INDEX IF NOT EXISTS idx_works_doi ON works(doi);

CREATE INDEX IF NOT EXISTS idx_api_queries_query_text ON api_queries(query_text);
CREATE INDEX IF NOT EXISTS idx_api_queries_created_at ON api_queries(created_at);

CREATE INDEX IF NOT EXISTS idx_works_api_queries_query_text ON works_api_queries(query_text);
CREATE INDEX IF NOT EXISTS idx_works_api_queries_work_id ON works_api_queries(work_id);
CREATE INDEX IF NOT EXISTS idx_works_api_queries_page_number ON works_api_queries(page_number);
CREATE INDEX IF NOT EXISTS idx_works_api_queries_created_at ON works_api_queries(created_at);

CREATE INDEX IF NOT EXISTS idx_authors_display_name ON authors(display_name);
CREATE INDEX IF NOT EXISTS idx_authors_works_count ON authors(works_count);
CREATE INDEX IF NOT EXISTS idx_authors_cited_by_count ON authors(cited_by_count);

CREATE INDEX IF NOT EXISTS idx_subfields_display_name ON subfields(display_name);
CREATE INDEX IF NOT EXISTS idx_subfields_works_count ON subfields(works_count);

CREATE INDEX IF NOT EXISTS idx_publishers_display_name ON publishers(display_name);
CREATE INDEX IF NOT EXISTS idx_publishers_works_count ON publishers(works_count);

CREATE INDEX IF NOT EXISTS idx_sources_display_name ON sources(display_name);
CREATE INDEX IF NOT EXISTS idx_sources_type ON sources(type);
CREATE INDEX IF NOT EXISTS idx_sources_is_oa ON sources(is_oa);

CREATE INDEX IF NOT EXISTS idx_funders_display_name ON funders(display_name);
CREATE INDEX IF NOT EXISTS idx_funders_works_count ON funders(works_count);

CREATE INDEX IF NOT EXISTS idx_institutions_display_name ON institutions(display_name);
CREATE INDEX IF NOT EXISTS idx_institutions_type ON institutions(type);
CREATE INDEX IF NOT EXISTS idx_institutions_country_code ON institutions(country_code);

CREATE INDEX IF NOT EXISTS idx_topics_display_name ON topics(display_name);
CREATE INDEX IF NOT EXISTS idx_topics_works_count ON topics(works_count);
CREATE INDEX IF NOT EXISTS idx_topics_cited_by_count ON topics(cited_by_count);

CREATE INDEX IF NOT EXISTS idx_concepts_display_name ON concepts(display_name);
CREATE INDEX IF NOT EXISTS idx_concepts_works_count ON concepts(works_count);
CREATE INDEX IF NOT EXISTS idx_concepts_cited_by_count ON concepts(cited_by_count);
CREATE INDEX IF NOT EXISTS idx_concepts_level ON concepts(level);

CREATE INDEX IF NOT EXISTS idx_domains_display_name ON domains(display_name);
CREATE INDEX IF NOT EXISTS idx_domains_works_count ON domains(works_count);
CREATE INDEX IF NOT EXISTS idx_domains_cited_by_count ON domains(cited_by_count);

CREATE INDEX IF NOT EXISTS idx_fields_display_name ON fields(display_name);
CREATE INDEX IF NOT EXISTS idx_fields_works_count ON fields(works_count);
CREATE INDEX IF NOT EXISTS idx_fields_cited_by_count ON fields(cited_by_count);

-- Author-Topic relationship table (denormalized from authors.topic_share)
CREATE TABLE IF NOT EXISTS author_topics (
    author_id VARCHAR NOT NULL,
    topic_id VARCHAR NOT NULL,
    value DOUBLE NOT NULL, -- from the value field in authors.topic_share
    PRIMARY KEY (author_id, topic_id)
);

CREATE INDEX IF NOT EXISTS idx_author_topics_author_id ON author_topics(author_id);
CREATE INDEX IF NOT EXISTS idx_author_topics_topic_id ON author_topics(topic_id);
CREATE INDEX IF NOT EXISTS idx_author_topics_value ON author_topics(value);

-- Author-Institution relationship table (denormalized from authors.affiliations)
CREATE TABLE IF NOT EXISTS author_affiliations (
    author_id VARCHAR NOT NULL,
    institution_id VARCHAR NOT NULL,
    years INTEGER[], -- array of years the author was affiliated with this institution
    PRIMARY KEY (author_id, institution_id)
);

CREATE INDEX IF NOT EXISTS idx_author_affiliations_author_id ON author_affiliations(author_id);
CREATE INDEX IF NOT EXISTS idx_author_affiliations_institution_id ON author_affiliations(institution_id);

-- Work-Source relationship table (denormalized from works.primary_location.source and works.locations)
CREATE TABLE IF NOT EXISTS work_sources (
    work_id VARCHAR NOT NULL,
    source_id VARCHAR NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE, -- TRUE if this is the primary_location source
    is_oa BOOLEAN,
    pdf_url VARCHAR,
    version VARCHAR, -- publishedVersion, acceptedVersion, submittedVersion
    is_accepted BOOLEAN,
    is_published BOOLEAN,
    PRIMARY KEY (work_id, source_id, is_primary)
);

CREATE INDEX IF NOT EXISTS idx_work_sources_work_id ON work_sources(work_id);
CREATE INDEX IF NOT EXISTS idx_work_sources_source_id ON work_sources(source_id);
CREATE INDEX IF NOT EXISTS idx_work_sources_is_primary ON work_sources(is_primary);
CREATE INDEX IF NOT EXISTS idx_work_sources_is_oa ON work_sources(is_oa);

-- Authorships relationship table (denormalized from works.authorships)
CREATE TABLE IF NOT EXISTS authorships (
    work_id VARCHAR NOT NULL,
    author_id VARCHAR NOT NULL,
    author_position VARCHAR, -- first, middle, last
    PRIMARY KEY (work_id, author_id)
);

CREATE INDEX IF NOT EXISTS idx_authorships_work_id ON authorships(work_id);
CREATE INDEX IF NOT EXISTS idx_authorships_author_id ON authorships(author_id);
CREATE INDEX IF NOT EXISTS idx_authorships_author_position ON authorships(author_position);

-- Work-Institution relationship table (denormalized from works.authorships.institutions)
CREATE TABLE IF NOT EXISTS work_institutions (
    work_id VARCHAR NOT NULL,
    author_id VARCHAR NOT NULL, -- which author is affiliated with this institution
    institution_id VARCHAR NOT NULL,
    PRIMARY KEY (work_id, author_id, institution_id)
);

CREATE INDEX IF NOT EXISTS idx_work_institutions_work_id ON work_institutions(work_id);
CREATE INDEX IF NOT EXISTS idx_work_institutions_author_id ON work_institutions(author_id);
CREATE INDEX IF NOT EXISTS idx_work_institutions_institution_id ON work_institutions(institution_id);