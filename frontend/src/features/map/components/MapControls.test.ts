import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import MapControls from './MapControls.vue'

describe('MapControls', () => {
  it('emits locate, compass and reset actions when ready', async () => {
    const wrapper = mount(MapControls, { props: { locating: false, disabled: false } })

    await wrapper.findAll('button')[0]?.trigger('click')
    await wrapper.findAll('button')[1]?.trigger('click')
    await wrapper.findAll('button')[2]?.trigger('click')

    expect(wrapper.emitted('locate')).toHaveLength(1)
    expect(wrapper.emitted('compass')).toHaveLength(1)
    expect(wrapper.emitted('reset')).toHaveLength(1)
  })

  it('disables controls while the map is unavailable', () => {
    const wrapper = mount(MapControls, { props: { locating: false, disabled: true } })

    expect(wrapper.findAll('button').every((button) => button.attributes('disabled') !== undefined)).toBe(true)
  })
})
