import { Button } from '@/components/ui/button'
import { api } from '@/api/client'

function App() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-100">
      <div className="flex flex-col items-center gap-4">
        <h1 className="text-3xl font-bold text-blue-600">Project8 DS2</h1>
        <p data-testid="api-url">{api.defaults.baseURL}</p>
        <Button>Click me</Button>
      </div>
    </div>
  )
}

export default App
