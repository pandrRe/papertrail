import polars as pl

work_schema = {
    # Identificadores básicos
    "id": pl.Utf8,
    "doi": pl.Utf8,
    "title": pl.Utf8,
    "display_name": pl.Utf8,
    "publication_year": pl.Int32,
    "publication_date": pl.Date,
    "language": pl.Utf8,
    "type": pl.Utf8,
    "type_crossref": pl.Utf8,
    # IDs object (struct)
    "ids": pl.Struct(
        {
            "openalex": pl.Utf8,
            "doi": pl.Utf8,
            "mag": pl.Int64,
            "pmid": pl.Utf8,
            "pmcid": pl.Utf8,
        }
    ),
    # Métricas de citação
    "cited_by_count": pl.Int32,
    "cited_by_api_url": pl.Utf8,
    "fwci": pl.Float64,
    # Citation normalized percentile (struct)
    "citation_normalized_percentile": pl.Struct(
        {
            "value": pl.Float64,
            "is_in_top_1_percent": pl.Boolean,
            "is_in_top_10_percent": pl.Boolean,
        }
    ),
    # Bibliografia (struct)
    "biblio": pl.Struct(
        {
            "volume": pl.Utf8,
            "issue": pl.Utf8,
            "first_page": pl.Utf8,
            "last_page": pl.Utf8,
        }
    ),
    # Open Access (struct)
    "open_access": pl.Struct(
        {
            "is_oa": pl.Boolean,
            "oa_status": pl.Utf8,  # gold, green, hybrid, bronze, closed, diamond
            "oa_url": pl.Utf8,
            "any_repository_has_fulltext": pl.Boolean,
        }
    ),
    # Primary location (struct complexo)
    "primary_location": pl.Struct(
        {
            "is_oa": pl.Boolean,
            "landing_page_url": pl.Utf8,
            "pdf_url": pl.Utf8,
            "license": pl.Utf8,
            "license_id": pl.Utf8,
            "version": pl.Utf8,  # publishedVersion, acceptedVersion, submittedVersion
            "is_accepted": pl.Boolean,
            "is_published": pl.Boolean,
            "source": pl.Struct(
                {
                    "id": pl.Utf8,
                    "display_name": pl.Utf8,
                    "issn_l": pl.Utf8,
                    "issn": pl.List(pl.Utf8),
                    "is_oa": pl.Boolean,
                    "is_in_doaj": pl.Boolean,
                    "is_indexed_in_scopus": pl.Boolean,
                    "is_core": pl.Boolean,
                    "host_organization": pl.Utf8,
                    "host_organization_name": pl.Utf8,
                    "host_organization_lineage": pl.List(pl.Utf8),
                    "host_organization_lineage_names": pl.List(pl.Utf8),
                    "type": pl.Utf8,  # journal, repository, conference
                }
            ),
        }
    ),
    # Best OA location (mesmo schema que primary_location)
    "best_oa_location": pl.Struct(
        {
            "is_oa": pl.Boolean,
            "landing_page_url": pl.Utf8,
            "pdf_url": pl.Utf8,
            "license": pl.Utf8,
            "license_id": pl.Utf8,
            "version": pl.Utf8,
            "is_accepted": pl.Boolean,
            "is_published": pl.Boolean,
            "source": pl.Struct(
                {
                    "id": pl.Utf8,
                    "display_name": pl.Utf8,
                    "issn_l": pl.Utf8,
                    "issn": pl.List(pl.Utf8),
                    "is_oa": pl.Boolean,
                    "is_in_doaj": pl.Boolean,
                    "is_indexed_in_scopus": pl.Boolean,
                    "is_core": pl.Boolean,
                    "host_organization": pl.Utf8,
                    "host_organization_name": pl.Utf8,
                    "host_organization_lineage": pl.List(pl.Utf8),
                    "host_organization_lineage_names": pl.List(pl.Utf8),
                    "type": pl.Utf8,
                }
            ),
        }
    ),
    # Locations (lista de structs)
    "locations": pl.List(
        pl.Struct(
            {
                "is_oa": pl.Boolean,
                "landing_page_url": pl.Utf8,
                "pdf_url": pl.Utf8,
                "license": pl.Utf8,
                "license_id": pl.Utf8,
                "version": pl.Utf8,
                "is_accepted": pl.Boolean,
                "is_published": pl.Boolean,
                "source": pl.Struct(
                    {
                        "id": pl.Utf8,
                        "display_name": pl.Utf8,
                        "issn_l": pl.Utf8,
                        "issn": pl.List(pl.Utf8),
                        "is_oa": pl.Boolean,
                        "is_in_doaj": pl.Boolean,
                        "is_indexed_in_scopus": pl.Boolean,
                        "is_core": pl.Boolean,
                        "host_organization": pl.Utf8,
                        "host_organization_name": pl.Utf8,
                        "host_organization_lineage": pl.List(pl.Utf8),
                        "host_organization_lineage_names": pl.List(pl.Utf8),
                        "type": pl.Utf8,
                    }
                ),
            }
        )
    ),
    "locations_count": pl.Int32,
    # Authorships (lista de structs)
    "authorships": pl.List(
        pl.Struct(
            {
                "author_position": pl.Utf8,  # first, middle, last
                "is_corresponding": pl.Boolean,
                "raw_author_name": pl.Utf8,
                "raw_affiliation_strings": pl.List(pl.Utf8),
                "author": pl.Struct(
                    {"id": pl.Utf8, "display_name": pl.Utf8, "orcid": pl.Utf8}
                ),
                "institutions": pl.List(
                    pl.Struct(
                        {
                            "id": pl.Utf8,
                            "display_name": pl.Utf8,
                            "ror": pl.Utf8,
                            "country_code": pl.Utf8,
                            "type": pl.Utf8,
                            "lineage": pl.List(pl.Utf8),
                        }
                    )
                ),
                "countries": pl.List(pl.Utf8),
                "affiliations": pl.List(
                    pl.Struct(
                        {
                            "raw_affiliation_string": pl.Utf8,
                            "institution_ids": pl.List(pl.Utf8),
                        }
                    )
                ),
            }
        )
    ),
    # Contadores de autoria
    "corresponding_author_ids": pl.List(pl.Utf8),
    "corresponding_institution_ids": pl.List(pl.Utf8),
    "countries_distinct_count": pl.Int32,
    "institutions_distinct_count": pl.Int32,
    # Topics (lista de structs)
    "topics": pl.List(
        pl.Struct(
            {
                "id": pl.Utf8,
                "display_name": pl.Utf8,
                "score": pl.Float64,
                "subfield": pl.Struct({"id": pl.Utf8, "display_name": pl.Utf8}),
                "field": pl.Struct({"id": pl.Utf8, "display_name": pl.Utf8}),
                "domain": pl.Struct({"id": pl.Utf8, "display_name": pl.Utf8}),
            }
        )
    ),
    # Primary topic (mesmo schema que item de topics)
    "primary_topic": pl.Struct(
        {
            "id": pl.Utf8,
            "display_name": pl.Utf8,
            "score": pl.Float64,
            "subfield": pl.Struct({"id": pl.Utf8, "display_name": pl.Utf8}),
            "field": pl.Struct({"id": pl.Utf8, "display_name": pl.Utf8}),
            "domain": pl.Struct({"id": pl.Utf8, "display_name": pl.Utf8}),
        }
    ),
    # Keywords (lista de structs)
    "keywords": pl.List(
        pl.Struct({"id": pl.Utf8, "display_name": pl.Utf8, "score": pl.Float64})
    ),
    # Concepts (lista de structs) - deprecated mas ainda presente
    "concepts": pl.List(
        pl.Struct(
            {
                "id": pl.Utf8,
                "wikidata": pl.Utf8,
                "display_name": pl.Utf8,
                "level": pl.Int32,
                "score": pl.Float64,
            }
        )
    ),
    # Sustainable Development Goals
    "sustainable_development_goals": pl.List(
        pl.Struct({"id": pl.Utf8, "display_name": pl.Utf8, "score": pl.Float64})
    ),
    # MeSH tags
    "mesh": pl.List(
        pl.Struct(
            {
                "descriptor_ui": pl.Utf8,
                "descriptor_name": pl.Utf8,
                "qualifier_ui": pl.Utf8,
                "qualifier_name": pl.Utf8,
                "is_major_topic": pl.Boolean,
            }
        )
    ),
    # APC (Article Processing Charges)
    "apc_list": pl.Struct(
        {
            "value": pl.Int32,
            "currency": pl.Utf8,
            "value_usd": pl.Int32,
            "provenance": pl.Utf8,
        }
    ),
    "apc_paid": pl.Struct(
        {
            "value": pl.Int32,
            "currency": pl.Utf8,
            "value_usd": pl.Int32,
            "provenance": pl.Utf8,
        }
    ),
    # Grants
    "grants": pl.List(
        pl.Struct(
            {"funder": pl.Utf8, "funder_display_name": pl.Utf8, "award_id": pl.Utf8}
        )
    ),
    # Referências e trabalhos relacionados
    "referenced_works": pl.List(pl.Utf8),
    "referenced_works_count": pl.Int32,
    "related_works": pl.List(pl.Utf8),
    # Abstract inverted index - armazena como JSON string
    # "abstract_inverted_index": pl.Utf8,  # Dinâmico - palavras como chaves (JSON string)
    # Counts by year
    "counts_by_year": pl.List(
        pl.Struct({"year": pl.Int32, "cited_by_count": pl.Int32})
    ),
    # Flags booleanos
    "has_fulltext": pl.Boolean,
    "fulltext_origin": pl.Utf8,  # pdf, ngrams
    "is_retracted": pl.Boolean,
    "is_paratext": pl.Boolean,
    # Indexed in
    "indexed_in": pl.List(pl.Utf8),  # crossref, doaj, pubmed, arxiv
    # Datasets e versions
    "datasets": pl.List(pl.Utf8),
    "versions": pl.List(pl.Utf8),
    # Institution assertions - armazena como JSON string
    "institution_assertions": pl.Utf8,  # Estrutura não documentada (JSON string)
    # Percentil de citação por ano
    "cited_by_percentile_year": pl.Struct({"min": pl.Int32, "max": pl.Int32}),
    # Datas de criação e atualização
    "created_date": pl.Date,
    "updated_date": pl.Datetime("us", "UTC"),
}

author_schema = {
    # Identificadores básicos
    "id": pl.Utf8,
    "orcid": pl.Utf8,
    "display_name": pl.Utf8,
    "display_name_alternatives": pl.List(pl.Utf8),
    # Métricas de produção
    "works_count": pl.Int32,
    "cited_by_count": pl.Int32,
    # Estatísticas resumidas (struct)
    "summary_stats": pl.Struct(
        {
            "2yr_mean_citedness": pl.Float64,
            "h_index": pl.Int32,
            "i10_index": pl.Int32,
        }
    ),
    # IDs object (struct) - todos os identificadores externos
    "ids": pl.Struct(
        {
            "openalex": pl.Utf8,
            "orcid": pl.Utf8,
            "scopus": pl.Utf8,
            "twitter": pl.Utf8,
            "wikipedia": pl.Utf8,
        }
    ),
    # Afiliações (lista de structs)
    "affiliations": pl.List(
        pl.Struct(
            {
                "institution": pl.Struct(
                    {
                        "id": pl.Utf8,
                        "ror": pl.Utf8,
                        "display_name": pl.Utf8,
                        "country_code": pl.Utf8,
                        "type": pl.Utf8,
                        "lineage": pl.List(pl.Utf8),
                    }
                ),
                "years": pl.List(pl.Int32),
            }
        )
    ),
    # Última instituição conhecida (lista de structs) - substituiu last_known_institution
    "last_known_institutions": pl.List(
        pl.Struct(
            {
                "id": pl.Utf8,
                "ror": pl.Utf8,
                "display_name": pl.Utf8,
                "country_code": pl.Utf8,
                "type": pl.Utf8,
                "lineage": pl.List(pl.Utf8),
            }
        )
    ),
    # Topics (lista de structs) - campo novo, não na documentação oficial mas presente nos dados
    "topics": pl.List(
        pl.Struct(
            {
                "id": pl.Utf8,
                "display_name": pl.Utf8,
                "count": pl.Int32,
                "subfield": pl.Struct(
                    {
                        "id": pl.Utf8,
                        "display_name": pl.Utf8,
                    }
                ),
                "field": pl.Struct(
                    {
                        "id": pl.Utf8,
                        "display_name": pl.Utf8,
                    }
                ),
                "domain": pl.Struct(
                    {
                        "id": pl.Utf8,
                        "display_name": pl.Utf8,
                    }
                ),
            }
        )
    ),
    # Topic share (lista de structs) - campo novo, não na documentação oficial mas presente nos dados
    "topic_share": pl.List(
        pl.Struct(
            {
                "id": pl.Utf8,
                "display_name": pl.Utf8,
                "value": pl.Float64,
                "subfield": pl.Struct(
                    {
                        "id": pl.Utf8,
                        "display_name": pl.Utf8,
                    }
                ),
                "field": pl.Struct(
                    {
                        "id": pl.Utf8,
                        "display_name": pl.Utf8,
                    }
                ),
                "domain": pl.Struct(
                    {
                        "id": pl.Utf8,
                        "display_name": pl.Utf8,
                    }
                ),
            }
        )
    ),
    # X concepts (lista de structs) - deprecated mas ainda presente
    "x_concepts": pl.List(
        pl.Struct(
            {
                "id": pl.Utf8,
                "wikidata": pl.Utf8,
                "display_name": pl.Utf8,
                "level": pl.Int32,
                "score": pl.Float64,
            }
        )
    ),
    # Counts by year (lista de structs)
    "counts_by_year": pl.List(
        pl.Struct(
            {
                "year": pl.Int32,
                "works_count": pl.Int32,
                "cited_by_count": pl.Int32,
            }
        )
    ),
    # API URLs
    "works_api_url": pl.Utf8,
    # Datas de criação e atualização
    "created_date": pl.Date,
    "updated_date": pl.Datetime("us", "UTC"),
}

subfields_schema = {
    # Identificadores básicos
    "id": pl.Utf8,
    "display_name": pl.Utf8,
    "description": pl.Utf8,
    "display_name_alternatives": pl.List(pl.Utf8),
    # IDs object (struct)
    "ids": pl.Struct(
        {
            "wikidata": pl.Utf8,
            "wikipedia": pl.Utf8,
        }
    ),
    # Hierarquia acadêmica
    "field": pl.Struct(
        {
            "id": pl.Utf8,
            "display_name": pl.Utf8,
        }
    ),
    "domain": pl.Struct(
        {
            "id": pl.Utf8,
            "display_name": pl.Utf8,
        }
    ),
    # Topics (lista de structs)
    "topics": pl.List(
        pl.Struct(
            {
                "id": pl.Utf8,
                "display_name": pl.Utf8,
            }
        )
    ),
    # Siblings (lista de structs)
    "siblings": pl.List(
        pl.Struct(
            {
                "id": pl.Utf8,
                "display_name": pl.Utf8,
            }
        )
    ),
    # Métricas
    "works_count": pl.Int64,
    "cited_by_count": pl.Int64,
    # API URLs
    "works_api_url": pl.Utf8,
    # Datas (como strings conforme dados reais)
    "updated_date": pl.Utf8,
    "created_date": pl.Utf8,
    "updated": pl.Utf8,
}

publisher_schema = {
    # Identificadores básicos
    "id": pl.Utf8,
    "display_name": pl.Utf8,
    # IDs object (struct)
    "ids": pl.Struct(
        {
            "openalex": pl.Utf8,
            "wikidata": pl.Utf8,
            "ror": pl.Utf8,
        }
    ),
    # Títulos e hierarquia
    "alternate_titles": pl.List(pl.Utf8),
    "parent_publisher": pl.Utf8,
    "lineage": pl.List(pl.Utf8),
    "hierarchy_level": pl.Int64,
    # Localização e URLs
    "country_codes": pl.List(pl.Utf8),
    "homepage_url": pl.Utf8,
    "image_url": pl.Utf8,
    "image_thumbnail_url": pl.Utf8,
    # Roles (lista de structs)
    "roles": pl.List(
        pl.Struct(
            {
                "role": pl.Utf8,
                "id": pl.Utf8,
                "works_count": pl.Int64,
            }
        )
    ),
    # Métricas básicas
    "works_count": pl.Int64,
    "cited_by_count": pl.Int64,
    "sources_count": pl.Int64,
    # Estatísticas resumidas (struct complexo)
    "summary_stats": pl.Struct(
        {
            "2yr_mean_citedness": pl.Float64,
            "h_index": pl.Int64,
            "i10_index": pl.Int64,
        }
    ),
    # Counts by year (lista de structs)
    "counts_by_year": pl.List(
        pl.Struct(
            {
                "year": pl.Int64,
                "works_count": pl.Int64,
                "oa_works_count": pl.Int64,
                "cited_by_count": pl.Int64,
            }
        )
    ),
    # X concepts (lista de structs) - deprecated mas ainda presente
    "x_concepts": pl.List(
        pl.Struct(
            {
                "id": pl.Utf8,
                "wikidata": pl.Utf8,
                "display_name": pl.Utf8,
                "level": pl.Int64,
                "score": pl.Float64,
            }
        )
    ),
    # API URLs
    "sources_api_url": pl.Utf8,
    # Datas (como strings conforme dados reais)
    "updated_date": pl.Utf8,
    "created_date": pl.Utf8,
    "updated": pl.Utf8,
}

source_schema = {
    # Identificadores básicos
    "id": pl.Utf8,
    "display_name": pl.Utf8,
    "abbreviated_title": pl.Utf8,
    # IDs object (struct)
    "ids": pl.Struct(
        {
            "openalex": pl.Utf8,
            "issn_l": pl.Utf8,
            "issn": pl.List(pl.Utf8),
            "mag": pl.Int64,
            "fatcat": pl.Utf8,
            "wikidata": pl.Utf8,
        }
    ),
    # ISSN information
    "issn_l": pl.Utf8,  # Canonical External ID
    "issn": pl.List(pl.Utf8),
    # Títulos alternativos
    "alternate_titles": pl.List(pl.Utf8),
    # Organização hospedeira
    "host_organization": pl.Utf8,
    "host_organization_name": pl.Utf8,
    "host_organization_lineage": pl.List(pl.Utf8),
    # Localização e URLs
    "country_code": pl.Utf8,
    "homepage_url": pl.Utf8,
    # Tipo e flags booleanos
    "type": pl.Utf8,  # journal, repository, conference, ebook platform, book series, metadata, other
    "is_oa": pl.Boolean,
    "is_in_doaj": pl.Boolean,
    "is_core": pl.Boolean,
    # Article Processing Charges
    "apc_prices": pl.List(
        pl.Struct(
            {
                "price": pl.Int32,
                "currency": pl.Utf8,
            }
        )
    ),
    "apc_usd": pl.Int32,
    # Sociedades
    "societies": pl.List(
        pl.Struct(
            {
                "url": pl.Utf8,
                "organization": pl.Utf8,
            }
        )
    ),
    # Estatísticas resumidas
    "summary_stats": pl.Struct(
        {
            "2yr_mean_citedness": pl.Float64,
            "h_index": pl.Int32,
            "i10_index": pl.Int32,
        }
    ),
    # Métricas básicas
    "works_count": pl.Int32,
    "cited_by_count": pl.Int32,
    # Counts by year (lista de structs)
    "counts_by_year": pl.List(
        pl.Struct(
            {
                "year": pl.Int32,
                "works_count": pl.Int32,
                "cited_by_count": pl.Int32,
            }
        )
    ),
    # X concepts (lista de structs) - deprecated mas ainda presente
    "x_concepts": pl.List(
        pl.Struct(
            {
                "id": pl.Utf8,
                "wikidata": pl.Utf8,
                "display_name": pl.Utf8,
                "level": pl.Int32,
                "score": pl.Float64,
            }
        )
    ),
    # API URLs
    "works_api_url": pl.Utf8,
    # Datas
    "created_date": pl.Utf8,
    "updated_date": pl.Utf8,
}

funders_schema = {
    # Identificadores básicos
    "id": pl.Utf8,
    "display_name": pl.Utf8,
    "description": pl.Utf8,
    # Títulos alternativos
    "alternate_titles": pl.List(pl.Utf8),
    # IDs object (struct)
    "ids": pl.Struct(
        {
            "openalex": pl.Utf8,
            "ror": pl.Utf8,
            "wikidata": pl.Utf8,
            "crossref": pl.Utf8,
            "doi": pl.Utf8,
        }
    ),
    # Localização e URLs
    "country_code": pl.Utf8,
    "homepage_url": pl.Utf8,
    "image_url": pl.Utf8,
    "image_thumbnail_url": pl.Utf8,
    # Contadores básicos
    "works_count": pl.Int32,
    "cited_by_count": pl.Int32,
    "grants_count": pl.Int32,
    # Estatísticas resumidas
    "summary_stats": pl.Struct(
        {
            "2yr_mean_citedness": pl.Float64,
            "h_index": pl.Int32,
            "i10_index": pl.Int32,
        }
    ),
    # Roles (lista de structs)
    "roles": pl.List(
        pl.Struct(
            {
                "role": pl.Utf8,  # funder, publisher, institution
                "id": pl.Utf8,
                "works_count": pl.Int32,
            }
        )
    ),
    # Counts by year (lista de structs)
    "counts_by_year": pl.List(
        pl.Struct(
            {
                "year": pl.Int32,
                "works_count": pl.Int32,
                "cited_by_count": pl.Int32,
            }
        )
    ),
    # Datas
    "created_date": pl.Utf8,
    "updated_date": pl.Utf8,
}

institutions_schema = {
    # Identificadores básicos
    "id": pl.Utf8,
    "ror": pl.Utf8,
    "display_name": pl.Utf8,
    "display_name_acronyms": pl.List(pl.Utf8),
    "display_name_alternatives": pl.List(pl.Utf8),
    # IDs object (struct)
    "ids": pl.Struct(
        {
            "openalex": pl.Utf8,
            "ror": pl.Utf8,
            "grid": pl.Utf8,
            "wikipedia": pl.Utf8,
            "wikidata": pl.Utf8,
            "mag": pl.Int64,
        }
    ),
    # Localização e geografia
    "country_code": pl.Utf8,
    "geo": pl.Struct(
        {
            "city": pl.Utf8,
            "geonames_city_id": pl.Utf8,
            "region": pl.Utf8,
            "country_code": pl.Utf8,
            "country": pl.Utf8,
            "latitude": pl.Float64,
            "longitude": pl.Float64,
        }
    ),
    # URLs e imagens
    "homepage_url": pl.Utf8,
    "image_url": pl.Utf8,
    "image_thumbnail_url": pl.Utf8,
    # Tipo e flags
    "type": pl.Utf8,  # education, healthcare, company, archive, nonprofit, government, facility, other
    "is_super_system": pl.Boolean,
    # Contadores básicos
    "works_count": pl.Int32,
    "cited_by_count": pl.Int32,
    # Estatísticas resumidas
    "summary_stats": pl.Struct(
        {
            "2yr_mean_citedness": pl.Float64,
            "h_index": pl.Int32,
            "i10_index": pl.Int32,
        }
    ),
    # Hierarquia e relacionamentos
    "lineage": pl.List(pl.Utf8),
    "associated_institutions": pl.List(
        pl.Struct(
            {
                "id": pl.Utf8,
                "ror": pl.Utf8,
                "display_name": pl.Utf8,
                "country_code": pl.Utf8,
                "type": pl.Utf8,
                "relationship": pl.Utf8,  # parent, child, related
            }
        )
    ),
    # Roles (lista de structs)
    "roles": pl.List(
        pl.Struct(
            {
                "role": pl.Utf8,  # institution, funder, publisher
                "id": pl.Utf8,
                "works_count": pl.Int32,
            }
        )
    ),
    # Repositórios
    "repositories": pl.List(
        pl.Struct(
            {
                "id": pl.Utf8,
                "display_name": pl.Utf8,
                "host_organization": pl.Utf8,
                "host_organization_name": pl.Utf8,
                "host_organization_lineage": pl.List(pl.Utf8),
            }
        )
    ),
    # Nomes internacionais
    "international": pl.Struct(
        {
            "display_name": pl.Utf8,  # JSON string representing arbitrary language code -> name dict
        }
    ),
    # Counts by year (lista de structs)
    "counts_by_year": pl.List(
        pl.Struct(
            {
                "year": pl.Int32,
                "works_count": pl.Int32,
                "cited_by_count": pl.Int32,
            }
        )
    ),
    # X concepts (lista de structs) - deprecated mas ainda presente
    "x_concepts": pl.List(
        pl.Struct(
            {
                "id": pl.Utf8,
                "wikidata": pl.Utf8,
                "display_name": pl.Utf8,
                "level": pl.Int32,
                "score": pl.Float64,
            }
        )
    ),
    # API URLs
    "works_api_url": pl.Utf8,
    # Datas
    "created_date": pl.Utf8,
    "updated_date": pl.Utf8,
}
