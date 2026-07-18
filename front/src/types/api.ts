export type Gender = '男' | '女'
export type Education = '高中' | '大专' | '本科' | '硕士' | '博士'
export type IncomeRange = '10万以下' | '10-20万' | '20-50万' | '50-100万' | '100万以上'
export type MarriageStatus = '未婚' | '离异' | '丧偶'
export type BodyType = '偏瘦' | '匀称' | '运动型' | '丰满'

export interface PartnerPreference {
  gender?: Gender; age_min?: number; age_max?: number
  height_min?: number; height_max?: number; education?: Education
  province?: string; city?: string; marriage_status?: MarriageStatus
}

export interface Profile {
  _id: string; user_id: string; nickname: string; gender: Gender
  birth_date: string; age: number; height: number; weight?: number
  province: string; city: string; education: Education; school?: string
  occupation: string; industry?: string; income_range?: IncomeRange
  body_type?: BodyType; marriage_status: MarriageStatus
  has_children: boolean; want_children?: boolean
  smoking?: boolean; drinking?: boolean
  self_intro?: string; interests: string[]; avatar_url?: string
  preference?: PartnerPreference; created_at: string
}

export interface ProfileCreate {
  user_id?: string; nickname: string; gender: Gender
  birth_date: string; height: number; weight?: number
  province: string; city: string; education: Education; school?: string
  occupation: string; industry?: string; income_range?: IncomeRange
  body_type?: BodyType; marriage_status: MarriageStatus
  has_children?: boolean; want_children?: boolean
  smoking?: boolean; drinking?: boolean
  self_intro?: string; interests?: string[]; avatar_url?: string
  preference?: PartnerPreference
}

export interface SearchResult { profile: Profile; score: number }
export interface PageResponse<T> { total: number; page: number; page_size: number; results: T[] }

export interface NaturalSearchParams {
  query: string; min_score?: number; use_query_optimization?: boolean
  use_rerank?: boolean; rerank_top_k?: number
  gender?: Gender; education?: Education; marriage_status?: MarriageStatus
  age_min?: number; age_max?: number; height_min?: number; height_max?: number
  province?: string; city?: string; occupation?: string
  page: number; page_size: number
}
export interface NaturalSearchResponse extends PageResponse<SearchResult> {
  optimized_query?: string; langfuse_trace_url?: string
}

export interface SearchParams {
  gender?: Gender; education?: Education; marriage_status?: MarriageStatus
  age_min?: number; age_max?: number; height_min?: number; height_max?: number
  province?: string; city?: string; occupation?: string
  page: number; page_size: number; sort_by?: string
}
export type SearchResponse = PageResponse<Profile>
