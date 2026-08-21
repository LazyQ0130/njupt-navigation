import axios from 'axios'
import { describe, expect, it } from 'vitest'
import { formatApiError } from './http'

describe('formatApiError', () => {
  it('returns the backend message when available', () => {
    const error = new axios.AxiosError(
      'bad request',
      'ERR_BAD_REQUEST',
      undefined,
      undefined,
      {
        data: { message: 'Geometry 不合法' },
        status: 400,
        statusText: 'Bad Request',
        headers: {},
        config: { headers: new axios.AxiosHeaders() },
      },
    )

    expect(formatApiError(error)).toBe('Geometry 不合法')
  })

  it('uses a safe fallback for unknown errors', () => {
    expect(formatApiError(new Error('secret details'))).toBe('加载地图基础数据失败，请稍后重试。')
  })
})

