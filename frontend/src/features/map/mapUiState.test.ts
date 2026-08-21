import { describe, expect, it } from 'vitest'
import { deriveMapUiState, geolocationErrorMessage } from './mapUiState'

describe('map UI state', () => {
  it('gives errors precedence after loading ends', () => {
    expect(deriveMapUiState(false, '网络错误', 2)).toBe('error')
    expect(deriveMapUiState(false, '', 0)).toBe('empty')
    expect(deriveMapUiState(false, '', 2)).toBe('ready')
  })

  it('maps browser geolocation errors to product guidance', () => {
    expect(geolocationErrorMessage(1)).toContain('权限')
    expect(geolocationErrorMessage(2)).toContain('定位服务')
    expect(geolocationErrorMessage(3)).toContain('超时')
  })
})
