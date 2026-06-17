/**
 * Code File type definitions based on backend Pydantic schemas
 */

export interface CodeFile {
  id: string
  project_id: string
  path: string
  content: string
  hash: string
  updated_at: string
  [key: string]: unknown
}

export interface CodeFileCreate {
  project_id: string
  path: string
  content: string
  file_hash: string
}

export interface CodeFileUpdate {
  content: string
  file_hash: string
}

export interface CodeFileResponse extends CodeFile {}

export interface CodeVersion {
  id: string
  code_file_id: string
  version_number: number
  content: string
  hash: string
  created_at: string
  [key: string]: unknown
}
