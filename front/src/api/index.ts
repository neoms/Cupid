import axios from 'axios'
import type {
  Profile,
  ProfileCreate,
  NaturalSearchParams,
  NaturalSearchResponse,
  SearchParams,
  SearchResponse,
} from '../types/api'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

export function createProfile(data: ProfileCreate) {
  return api.post<Profile>('/profiles', data)
}

export function searchProfiles(params: SearchParams) {
  return api.post<SearchResponse>('/profiles/search', params)
}

export function naturalSearch(params: NaturalSearchParams) {
  return api.post<NaturalSearchResponse>('/profiles/search/natural', params)
}

export function healthCheck() {
  return api.get('/health')
}
