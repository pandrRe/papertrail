CREATE TABLE IF NOT EXISTS works (
    -- Basic identifiers
    id VARCHAR PRIMARY KEY,
    doi VARCHAR,
    title VARCHAR,
    display_name VARCHAR,
    publication_year INTEGER,
    publication_date DATE,
    language VARCHAR,
    type VARCHAR,
    type_crossref VARCHAR,
    
    -- IDs object
    ids STRUCT(
        openalex VARCHAR,
        doi VARCHAR,
        mag BIGINT,
        pmid VARCHAR,
        pmcid VARCHAR
    ),
    
    -- Citation metrics
    cited_by_count INTEGER,
    cited_by_api_url VARCHAR,
    fwci DOUBLE,
    
    -- Citation normalized percentile
    citation_normalized_percentile STRUCT(
        value DOUBLE,
        is_in_top_1_percent BOOLEAN,
        is_in_top_10_percent BOOLEAN
    ),
    
    -- Bibliography
    biblio STRUCT(
        volume VARCHAR,
        issue VARCHAR,
        first_page VARCHAR,
        last_page VARCHAR
    ),
    
    -- Open Access
    open_access STRUCT(
        is_oa BOOLEAN,
        oa_status VARCHAR, -- gold, green, hybrid, bronze, closed, diamond
        oa_url VARCHAR,
        any_repository_has_fulltext BOOLEAN
    ),
    
    -- Primary location
    primary_location STRUCT(
        is_oa BOOLEAN,
        landing_page_url VARCHAR,
        pdf_url VARCHAR,
        license VARCHAR,
        license_id VARCHAR,
        version VARCHAR, -- publishedVersion, acceptedVersion, submittedVersion
        is_accepted BOOLEAN,
        is_published BOOLEAN,
        source STRUCT(
            id VARCHAR,
            display_name VARCHAR,
            issn_l VARCHAR,
            issn VARCHAR[],
            is_oa BOOLEAN,
            is_in_doaj BOOLEAN,
            is_indexed_in_scopus BOOLEAN,
            is_core BOOLEAN,
            host_organization VARCHAR,
            host_organization_name VARCHAR,
            host_organization_lineage VARCHAR[],
            host_organization_lineage_names VARCHAR[],
            type VARCHAR -- journal, repository, conference
        )
    ),
    
    -- Best OA location (same schema as primary_location)
    best_oa_location STRUCT(
        is_oa BOOLEAN,
        landing_page_url VARCHAR,
        pdf_url VARCHAR,
        license VARCHAR,
        license_id VARCHAR,
        version VARCHAR,
        is_accepted BOOLEAN,
        is_published BOOLEAN,
        source STRUCT(
            id VARCHAR,
            display_name VARCHAR,
            issn_l VARCHAR,
            issn VARCHAR[],
            is_oa BOOLEAN,
            is_in_doaj BOOLEAN,
            is_indexed_in_scopus BOOLEAN,
            is_core BOOLEAN,
            host_organization VARCHAR,
            host_organization_name VARCHAR,
            host_organization_lineage VARCHAR[],
            host_organization_lineage_names VARCHAR[],
            type VARCHAR
        )
    ),
    
    -- Locations (list of structs) - OPTIONAL
    locations STRUCT(
        is_oa BOOLEAN,
        landing_page_url VARCHAR,
        pdf_url VARCHAR,
        license VARCHAR,
        license_id VARCHAR,
        version VARCHAR,
        is_accepted BOOLEAN,
        is_published BOOLEAN,
        source STRUCT(
            id VARCHAR,
            display_name VARCHAR,
            issn_l VARCHAR,
            issn VARCHAR[],
            is_oa BOOLEAN,
            is_in_doaj BOOLEAN,
            is_indexed_in_scopus BOOLEAN,
            is_core BOOLEAN,
            host_organization VARCHAR,
            host_organization_name VARCHAR,
            host_organization_lineage VARCHAR[],
            host_organization_lineage_names VARCHAR[],
            type VARCHAR
        )
    )[],
    locations_count INTEGER,
    
    -- Authorships (list of structs) - OPTIONAL
    authorships STRUCT(
        author_position VARCHAR, -- first, middle, last
        is_corresponding BOOLEAN,
        raw_author_name VARCHAR,
        raw_affiliation_strings VARCHAR[],
        author STRUCT(
            id VARCHAR,
            display_name VARCHAR,
            orcid VARCHAR
        ),
        institutions STRUCT(
            id VARCHAR,
            display_name VARCHAR,
            ror VARCHAR,
            country_code VARCHAR,
            type VARCHAR,
            lineage VARCHAR[]
        )[],
        countries VARCHAR[],
        affiliations STRUCT(
            raw_affiliation_string VARCHAR,
            institution_ids VARCHAR[]
        )[]
    )[],
    
    -- Authorship counters
    corresponding_author_ids VARCHAR[],
    corresponding_institution_ids VARCHAR[],
    countries_distinct_count INTEGER,
    institutions_distinct_count INTEGER,
    
    -- Topics (list of structs) - OPTIONAL
    topics STRUCT(
        id VARCHAR,
        display_name VARCHAR,
        score DOUBLE,
        subfield STRUCT(id VARCHAR, display_name VARCHAR),
        field STRUCT(id VARCHAR, display_name VARCHAR),
        domain STRUCT(id VARCHAR, display_name VARCHAR)
    )[],
    
    -- Primary topic
    primary_topic STRUCT(
        id VARCHAR,
        display_name VARCHAR,
        score DOUBLE,
        subfield STRUCT(id VARCHAR, display_name VARCHAR),
        field STRUCT(id VARCHAR, display_name VARCHAR),
        domain STRUCT(id VARCHAR, display_name VARCHAR)
    ),
    
    -- Keywords (list of structs) - OPTIONAL
    keywords STRUCT(
        id VARCHAR,
        display_name VARCHAR,
        score DOUBLE
    )[],
    
    -- Concepts (deprecated but still present) - OPTIONAL
    concepts STRUCT(
        id VARCHAR,
        wikidata VARCHAR,
        display_name VARCHAR,
        level INTEGER,
        score DOUBLE
    )[],
    
    -- Sustainable Development Goals - OPTIONAL
    sustainable_development_goals STRUCT(
        id VARCHAR,
        display_name VARCHAR,
        score DOUBLE
    )[],
    
    -- MeSH tags - OPTIONAL
    mesh STRUCT(
        descriptor_ui VARCHAR,
        descriptor_name VARCHAR,
        qualifier_ui VARCHAR,
        qualifier_name VARCHAR,
        is_major_topic BOOLEAN
    )[],
    
    -- APC (Article Processing Charges)
    apc_list STRUCT(
        value INTEGER,
        currency VARCHAR,
        value_usd INTEGER,
        provenance VARCHAR
    ),
    apc_paid STRUCT(
        value INTEGER,
        currency VARCHAR,
        value_usd INTEGER,
        provenance VARCHAR
    ),
    
    -- Grants - OPTIONAL
    grants STRUCT(
        funder VARCHAR,
        funder_display_name VARCHAR,
        award_id VARCHAR
    )[],
    
    -- References and related works - OPTIONAL
    referenced_works VARCHAR[],
    referenced_works_count INTEGER,
    related_works VARCHAR[],
    
    -- Abstract inverted index (stored as JSON string)
    abstract_inverted_index VARCHAR, -- JSON string
    
    -- Counts by year - OPTIONAL
    counts_by_year STRUCT(
        year INTEGER,
        cited_by_count INTEGER
    )[],
    
    -- Boolean flags
    has_fulltext BOOLEAN,
    fulltext_origin VARCHAR, -- pdf, ngrams
    is_retracted BOOLEAN,
    is_paratext BOOLEAN,
    
    -- Indexed in - OPTIONAL
    indexed_in VARCHAR[], -- crossref, doaj, pubmed, arxiv
    
    -- Datasets and versions - OPTIONAL
    datasets VARCHAR[],
    versions VARCHAR[],
    
    -- Institution assertions (stored as JSON string)
    institution_assertions VARCHAR, -- JSON string
    
    -- Citation percentile by year
    cited_by_percentile_year STRUCT(
        min INTEGER,
        max INTEGER
    ),
    
    -- Timestamps
    created_date DATE,
    updated_date TIMESTAMPTZ
);