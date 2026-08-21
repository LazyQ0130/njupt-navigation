export type MapUiState = 'loading' | 'error' | 'empty' | 'ready'

export function deriveMapUiState(
  loading: boolean,
  error: string,
  featureCount: number,
): MapUiState {
  if (loading) return 'loading'
  if (error) return 'error'
  if (featureCount === 0) return 'empty'
  return 'ready'
}

export function geolocationErrorMessage(code: number): string {
  if (code === 1) return '定位权限未开启，请在浏览器设置中允许访问位置。'
  if (code === 2) return '暂时无法获取当前位置，请确认系统定位服务已开启。'
  if (code === 3) return '定位请求超时，请移动到开阔区域后重试。'
  return '定位失败，请稍后重试。'
}
