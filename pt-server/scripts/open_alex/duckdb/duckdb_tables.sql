-- DuckDB table definitions for OpenAlex entities (excluding works)
-- Authors table
DROP TABLE IF EXISTS author_topics;
DROP TABLE IF EXISTS author_affiliations;
DROP TABLE IF EXISTS authors;
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
    PRIMARY KEY (author_id, topic_id),
    FOREIGN KEY (author_id) REFERENCES authors(id),
    FOREIGN KEY (topic_id) REFERENCES topics(id)
);

CREATE INDEX IF NOT EXISTS idx_author_topics_author_id ON author_topics(author_id);
CREATE INDEX IF NOT EXISTS idx_author_topics_topic_id ON author_topics(topic_id);
CREATE INDEX IF NOT EXISTS idx_author_topics_value ON author_topics(value);

-- Author-Institution relationship table (denormalized from authors.affiliations)
CREATE TABLE IF NOT EXISTS author_affiliations (
    author_id VARCHAR NOT NULL,
    institution_id VARCHAR NOT NULL,
    years INTEGER[], -- array of years the author was affiliated with this institution
    PRIMARY KEY (author_id, institution_id),
    FOREIGN KEY (author_id) REFERENCES authors(id),
    FOREIGN KEY (institution_id) REFERENCES institutions(id)
);

CREATE INDEX IF NOT EXISTS idx_author_affiliations_author_id ON author_affiliations(author_id);
CREATE INDEX IF NOT EXISTS idx_author_affiliations_institution_id ON author_affiliations(institution_id);