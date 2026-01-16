/**
 * ORCID API Integration Module
 * 
 * This module provides functions to read public ORCID records using the ORCID Public API.
 * It implements the client credentials OAuth flow and supports reading full records
 * and specific sections like works, employment, education, etc.
 * 
 * @see https://info.orcid.org/documentation/api-tutorials/api-tutorial-read-data-on-a-record/
 */

import { getCachedValue, putCachedValue } from "./cache";

// Environment validation
const ORCID_CLIENT_ID = process.env.ORCID_CLIENT_ID;
const ORCID_CLIENT_SECRET = process.env.ORCID_CLIENT_SECRET;

if (!ORCID_CLIENT_ID || !ORCID_CLIENT_SECRET) {
  throw new Error('ORCID_CLIENT_ID and ORCID_CLIENT_SECRET environment variables are required');
}

// ORCID API configuration
const ORCID_BASE_URL = 'https://orcid.org';
const ORCID_API_BASE_URL = 'https://pub.orcid.org/v3.0';
const TOKEN_ENDPOINT = `${ORCID_BASE_URL}/oauth/token`;

// TypeScript types for ORCID API responses
export interface OrcidTokenResponse {
  access_token: string;
  token_type: string;
  refresh_token: string;
  expires_in: number;
  scope: string;
  orcid: string | null;
}

export interface OrcidError {
  error: string;
  error_description?: string;
}

// Common elements used throughout ORCID schema
export interface OrcidDate {
  year: { value: string }; // ISO year string
  month?: { value: string }; // ISO month string
  day?: { value: string }; // ISO day string
}

export interface OrcidCreatedDate {
  value: string; // ISO date string
}

export interface OrcidLastModifiedDate {
  value: string; // ISO date string  
}

export interface OrcidIdentifier {
  uri: string;
  path: string;
  host: string;
}

export interface OrcidSource {
  'source-orcid'?: OrcidIdentifier & {
    'source-name'?: string;
  };
  'source-client-id'?: OrcidIdentifier & {
    'source-name'?: string;
  };
}

export interface OrcidExternalId {
  'external-id-type': string;
  'external-id-value': string;
  'external-id-url'?: string;
  'external-id-relationship': 'self' | 'part-of' | 'version-of';
}

export interface OrcidAddress {
  city: string;
  region?: string;
  country: string;
}

export interface OrcidOrganization {
  name: string;
  address: OrcidAddress;
  'disambiguated-organization'?: {
    'disambiguated-organization-identifier': string;
    'disambiguation-source': string;
  };
}

// Person section types
export interface OrcidPersonName {
  'given-names': string;
  'family-name'?: string;
  'credit-name'?: string;
}

export interface OrcidName {
  'created-date': OrcidCreatedDate;
  'last-modified-date': OrcidLastModifiedDate;
  'given-names': string;
  'family-name'?: string; 
  'credit-name'?: string;
  visibility: 'public' | 'limited' | 'private';
}

export interface OrcidOtherName {
  'put-code': number;
  'created-date': OrcidCreatedDate;
  'last-modified-date': OrcidLastModifiedDate;
  source: OrcidSource;
  content: string;
  visibility: 'public' | 'limited' | 'private';
  path: string;
  'display-index': number;
}

export interface OrcidBiography {
  'created-date': OrcidCreatedDate;
  'last-modified-date': OrcidLastModifiedDate;
  content: string;
  visibility: 'public' | 'limited' | 'private';
  path: string;
}

export interface OrcidResearcherUrl {
  'put-code': number;
  'created-date': OrcidCreatedDate;
  'last-modified-date': OrcidLastModifiedDate;
  source: OrcidSource;
  'url-name'?: string;
  url: string;
  visibility: 'public' | 'limited' | 'private';
  path: string;
  'display-index': number;
}

export interface OrcidKeyword {
  'put-code': number;
  'created-date': OrcidCreatedDate;
  'last-modified-date': OrcidLastModifiedDate;
  source: OrcidSource;
  content: string;
  visibility: 'public' | 'limited' | 'private';
  path: string;
  'display-index': number;
}

export interface OrcidCountryAddress {
  'put-code': number;
  'created-date': OrcidCreatedDate;
  'last-modified-date': OrcidLastModifiedDate;
  source: OrcidSource;
  country: string; // ISO 3166-1 alpha-2 format
  visibility: 'public' | 'limited' | 'private';
  path: string;
  'display-index': number;
}

export interface OrcidPersonExternalId {
  'put-code': number;
  'created-date': OrcidCreatedDate;
  'last-modified-date': OrcidLastModifiedDate;
  source: OrcidSource;
  'external-id-type': string;
  'external-id-value': string;
  'external-id-url'?: string;
  'external-id-relationship': 'self';
  visibility: 'public' | 'limited' | 'private';
  path: string;
  'display-index': number;
}

export interface OrcidEmailAddress {
  'created-date': OrcidCreatedDate;
  'last-modified-date': OrcidLastModifiedDate;
  source: OrcidSource;
  email: string;
  visibility: 'public' | 'limited' | 'private';
  verified?: boolean;
  primary?: boolean;
}

// Activities section types
export interface OrcidWorkSummary {
  'put-code': number;
  'created-date': OrcidCreatedDate;
  'last-modified-date': OrcidLastModifiedDate;
  source: OrcidSource;
  title: {
    title: string;
    subtitle?: string;
    'translated-title'?: {
      value: string;
      'language-code': string;
    };
  };
  'external-ids'?: {
    'external-id': OrcidExternalId[];
  };
  type: string;
  'publication-date'?: OrcidDate;
  'journal-title'?: string;
  visibility: 'public' | 'limited' | 'private';
  path: string;
  'display-index': number;
}

export interface OrcidEmploymentSummary {
  'put-code': number;
  'created-date': OrcidCreatedDate;
  'last-modified-date': OrcidLastModifiedDate;
  source: OrcidSource;
  'department-name'?: string;
  'role-title'?: string;
  'start-date'?: OrcidDate;
  'end-date'?: OrcidDate;
  organization: OrcidOrganization;
  visibility: 'public' | 'limited' | 'private';
  path: string;
}

export interface OrcidEducationSummary {
  'put-code': number;
  'created-date': OrcidCreatedDate;
  'last-modified-date': OrcidLastModifiedDate;
  source: OrcidSource;
  'department-name'?: string;
  'role-title'?: string;
  'start-date'?: OrcidDate;
  'end-date'?: OrcidDate;
  organization: OrcidOrganization;
  visibility: 'public' | 'limited' | 'private';
  path: string;
}

export interface OrcidFundingSummary {
  'put-code': number;
  'created-date': OrcidCreatedDate;
  'last-modified-date': OrcidLastModifiedDate;
  source: OrcidSource;
  title: {
    title: string;
  };
  'external-ids'?: {
    'external-id': OrcidExternalId[];
  };
  type: string;
  'start-date'?: OrcidDate;
  'end-date'?: OrcidDate;
  visibility: 'public' | 'limited' | 'private';
  path: string;
  'display-index': number;
}

// Main record structure
export interface OrcidRecord {
  'orcid-identifier': OrcidIdentifier;
  preferences?: {
    locale: string;
  };
  history?: {
    'creation-method': 'Direct' | 'Website' | 'Member-referred' | 'API';
    'creation-date'?: string;
    'submission-date': string;
    'last-modified-date': OrcidLastModifiedDate;
    claimed: boolean;
    'verified-email': boolean;
    'verified-primary-email': boolean;
  };
  person?: {
    'last-modified-date': OrcidLastModifiedDate;
    name?: OrcidName;
    'other-names'?: {
      'last-modified-date': OrcidLastModifiedDate;
      'other-name': OrcidOtherName[];
      path: string;
    };
    biography?: OrcidBiography;
    'researcher-urls'?: {
      'last-modified-date': OrcidLastModifiedDate;
      'researcher-url': OrcidResearcherUrl[];
      path: string;
    };
    emails?: {
      'last-modified-date': OrcidLastModifiedDate;
      email: OrcidEmailAddress[];
      path: string;
    };
    addresses?: {
      'last-modified-date': OrcidLastModifiedDate;
      address: OrcidCountryAddress[];
      path: string;
    };
    keywords?: {
      'last-modified-date': OrcidLastModifiedDate;
      keyword: OrcidKeyword[];
      path: string;
    };
    'external-identifiers'?: {
      'last-modified-date': OrcidLastModifiedDate;
      'external-identifier': OrcidPersonExternalId[];
      path: string;
    };
    path: string;
  };
  'activities-summary'?: {
    'last-modified-date': OrcidLastModifiedDate;
    works?: {
      'last-modified-date': OrcidLastModifiedDate;
      group: Array<{
        'last-modified-date': OrcidLastModifiedDate;
        'external-ids'?: {
          'external-id': OrcidExternalId[];
        };
        'work-summary': OrcidWorkSummary[];
      }>;
      path: string;
    };
    employments?: {
      'last-modified-date': OrcidLastModifiedDate;
      'affiliation-group': Array<{
        'last-modified-date': OrcidLastModifiedDate;
        'external-ids'?: {
          'external-id': OrcidExternalId[];
        };
        summaries: {
          'employment-summary': OrcidEmploymentSummary[];
        }[];
      }>;
      path: string;
    };
    educations?: {
      'last-modified-date': OrcidLastModifiedDate;
      'affiliation-group': Array<{
        'last-modified-date': OrcidLastModifiedDate;
        'external-ids'?: {
          'external-id': OrcidExternalId[];
        };
        'education-summary': OrcidEducationSummary[];
      }>;
      path: string;
    };
    fundings?: {
      'last-modified-date': OrcidLastModifiedDate;
      group: Array<{
        'last-modified-date': OrcidLastModifiedDate;
        'external-ids'?: {
          'external-id': OrcidExternalId[];
        };
        'funding-summary': OrcidFundingSummary[];
      }>;
      path: string;
    };
    path: string;
  };
}

export class OrcidApiError extends Error {
  constructor(
    message: string,
    public status?: number,
    public orcidError?: OrcidError
  ) {
    super(message);
    this.name = 'OrcidApiError';
  }
}

/**
 * Validates ORCID ID format (0000-0000-0000-0000)
 */
export function validateOrcidId(orcidId: string): boolean {
  const orcidRegex = /^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$/;
  return orcidRegex.test(orcidId);
}

/**
 * Normalizes ORCID ID to standard format
 * Handles URLs and variations
 */
export function normalizeOrcidId(orcidId: string): string {
  // Remove ORCID URL prefix if present
  const cleanId = orcidId.replace(/^https?:\/\/(www\.)?orcid\.org\//, '');
  
  // Validate format
  if (!validateOrcidId(cleanId)) {
    throw new OrcidApiError(`Invalid ORCID ID format: ${orcidId}`);
  }
  
  return cleanId;
}

/**
 * Obtains an access token using client credentials OAuth flow
 * Tokens are cached since they have a very long expiration (20+ years)
 */
export async function getAccessToken(): Promise<string> {
  const CACHE_TTL = 1000 * 60 * 60 * 24 * 365 * 20; // 20 years
  const token = getCachedValue<string>('orcid_access_token');

  if (token) {
    return Promise.resolve(token);
  }

  try {
    const response = await fetch(TOKEN_ENDPOINT, {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        client_id: ORCID_CLIENT_ID!,
        client_secret: ORCID_CLIENT_SECRET!,
        grant_type: 'client_credentials',
        scope: '/read-public',
      }),
    });

    if (!response.ok) {
      const errorData = await response.json() as OrcidError;
      throw new OrcidApiError(
        `Failed to get access token: ${errorData.error_description || errorData.error}`,
        response.status,
        errorData
      );
    }

    const tokenData = await response.json() as OrcidTokenResponse;
    
    putCachedValue('orcid_access_token', tokenData.access_token, CACHE_TTL);

    return tokenData.access_token;
  } catch (error) {
    if (error instanceof OrcidApiError) {
      throw error;
    }
    throw new OrcidApiError(`Network error while getting access token: ${error}`);
  }
}

/**
 * Makes an authenticated request to the ORCID API
 */
async function makeOrcidRequest(endpoint: string): Promise<any> {
  const token = await getAccessToken();
  
  const response = await fetch(`${ORCID_API_BASE_URL}${endpoint}`, {
    method: 'GET',
    headers: {
      'Accept': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    if (response.status === 404) {
      throw new OrcidApiError('ORCID record not found or not public', 404);
    }
    
    let errorData: OrcidError;
    try {
      errorData = await response.json() as OrcidError;
    } catch {
      errorData = { error: `HTTP ${response.status}` };
    }
    
    throw new OrcidApiError(
      `ORCID API error: ${errorData.error_description || errorData.error}`,
      response.status,
      errorData
    );
  }

  return response.json();
}

/**
 * Reads the complete ORCID record for a given ORCID ID
 * Returns the full record summary including activities
 */
export async function readOrcidRecord(orcidId: string): Promise<OrcidRecord> {
  const normalizedId = normalizeOrcidId(orcidId);
  const cacheKey = `orcid_record_${normalizedId}`;
  const cachedRecord = getCachedValue<OrcidRecord>(cacheKey);
  if (cachedRecord) {
    return cachedRecord;
  }

  const record = await makeOrcidRequest(`/${normalizedId}`);
  putCachedValue(cacheKey, record);

  return makeOrcidRequest(`/${normalizedId}/record`);
}
