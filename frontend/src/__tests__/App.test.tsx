import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import App from '@/App'

describe('App', () => {
  it('renders the heading, button, and api url', () => {
    render(<App />)
    expect(screen.getByRole('heading', { name: 'Project8 DS2' })).toBeVisible()
    expect(screen.getByRole('button', { name: 'Click me' })).toBeVisible()
    expect(screen.getByTestId('api-url')).toBeVisible()
  })
})
