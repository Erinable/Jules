/**
 * User type definitions based on backend Pydantic schemas
 */

export interface User {
  id: string
  email: string
  name: string
  created_at: string
}

export interface UserCreate {
  email: string
  name: string
}

export interface UserUpdate {
  name: string
}

export interface UserResponse extends User {}
