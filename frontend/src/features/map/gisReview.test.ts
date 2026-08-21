import { describe, expect, it } from 'vitest'
import { activeReviewLayerKeys, isGisReviewModeEnabled } from './gisReview'

describe('GIS review mode', () => {
  it('is disabled by default and in production builds without an explicit flag', () => {
    expect(isGisReviewModeEnabled('', true)).toBe(false)
    expect(isGisReviewModeEnabled('?debug=gisp1', false)).toBe(false)
    expect(activeReviewLayerKeys(false)).toEqual([])
  })

  it('loads debug layers only when the build and URL both enable review mode', () => {
    expect(isGisReviewModeEnabled('?debug=gisp1', true)).toBe(true)
    expect(activeReviewLayerKeys(true)).toContain('topology-gaps')
    expect(activeReviewLayerKeys(true)).toContain('candidate-entrances')
  })
})
