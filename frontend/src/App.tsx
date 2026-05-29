import { useState, useEffect } from 'react'
import './App.css'

const API_BASE = 'http://localhost:8000/api/v1'

interface ChemicalListItem {
  cas_number: string
  name: string
  formula: string | null
  state_at_ambient: string | null
  hazard_class: string | null
}

interface ChemicalDetail extends ChemicalListItem {
  molecular_weight: number
  boiling_point_c: number | null
  gas_density_ratio: number | null
  is_heavier_than_air: boolean | null
  erpg_1_ppm: number | null
  erpg_2_ppm: number | null
  erpg_3_ppm: number | null
  idlh_ppm: number | null
  aegl_1_60min_ppm: number | null
  aegl_2_60min_ppm: number | null
  aegl_3_60min_ppm: number | null
  [key: string]: unknown
}

interface ZoneResult {
  threshold_name: string
  threshold_value_ppm: number | null
  threshold_value_mg_m3: number | null
  downwind_distance_m: number | null
  crosswind_width_m: number | null
  area_km2: number | null
}

interface CalcResult {
  model_used: string
  model_description: string
  computation_time_ms: number
  wind_direction_deg: number
  stability_class: string
  total_affected_area_km2: number
  zones: ZoneResult[]
  warnings: string[] | null
}

function App() {
  const [chemicals, setChemicals] = useState<ChemicalListItem[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedChemical, setSelectedChemical] = useState<ChemicalDetail | null>(null)
  const [calcResult, setCalcResult] = useState<CalcResult | null>(null)
  const [loading, setLoading] = useState(false)

  // Calculation inputs
  const [releaseRate, setReleaseRate] = useState(1.0)
  const [windSpeed, setWindSpeed] = useState(5.0)
  const [stabilityClass, setStabilityClass] = useState('D')
  const [windDirection, setWindDirection] = useState(0)
  const [releaseHeight, setReleaseHeight] = useState(0)
  const [scenarioType, setScenarioType] = useState('continuous')
  const [totalRelease, setTotalRelease] = useState(1000)

  useEffect(() => {
    fetchChemicals()
  }, [])

  const fetchChemicals = async () => {
    try {
      const res = await fetch(`${API_BASE}/chemicals/?limit=100`)
      const data = await res.json()
      setChemicals(data)
    } catch (err) {
      console.error('Failed to fetch chemicals:', err)
    }
  }

  const searchChemicals = async () => {
    if (searchQuery.length < 2) return
    try {
      const res = await fetch(`${API_BASE}/chemicals/search?q=${encodeURIComponent(searchQuery)}`)
      const data = await res.json()
      setChemicals(data.chemicals)
    } catch (err) {
      console.error('Search failed:', err)
    }
  }

  const selectChemical = async (cas: string) => {
    try {
      const res = await fetch(`${API_BASE}/chemicals/${cas}`)
      const data = await res.json()
      setSelectedChemical(data)
    } catch (err) {
      console.error('Failed to fetch chemical:', err)
    }
  }

  const calculateEPZ = async () => {
    if (!selectedChemical) return
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/calculations/compute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chemical_cas: selectedChemical.cas_number,
          scenario_type: scenarioType,
          release_rate_kg_s: scenarioType === 'continuous' ? releaseRate : undefined,
          total_release_kg: scenarioType !== 'continuous' ? totalRelease : undefined,
          duration_s: scenarioType !== 'continuous' ? 600 : undefined,
          release_height_m: releaseHeight,
          stability_class: stabilityClass,
          wind_speed_ms: windSpeed,
          wind_direction_deg: windDirection,
        }),
      })
      const data = await res.json()
      setCalcResult(data.result)
    } catch (err) {
      console.error('Calculation failed:', err)
    }
    setLoading(false)
  }

  const formatDistance = (m: number | null) => {
    if (m === null) return 'N/A'
    return m >= 1000 ? `${(m / 1000).toFixed(2)} km` : `${m.toFixed(1)} m`
  }

  const formatArea = (km2: number | null) => {
    if (km2 === null) return 'N/A'
    return km2 >= 1 ? `${km2.toFixed(2)} km²` : `${(km2 * 1e6).toFixed(0)} m²`
  }

  const zoneColors: Record<string, string> = {
    erpg_3: '#ef4444',
    idlh: '#dc2626',
    erpg_2: '#f97316',
    erpg_1: '#eab308',
    aegl_3_60min: '#b91c1c',
    aegl_2_60min: '#c2410c',
    aegl_1_60min: '#a16207',
  }

  return (
    <div className="app">
      <header className="header">
        <h1>☢️ ToxZone</h1>
        <p>Emergency Exposure Boundary Planner</p>
      </header>

      <div className="main-grid">
        {/* Chemical Search Panel */}
        <div className="panel">
          <h2>Chemical Database</h2>
          <div className="search-box">
            <input
              type="text"
              placeholder="Search by name, CAS, or formula..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && searchChemicals()}
            />
            <button onClick={searchChemicals}>Search</button>
            <button onClick={fetchChemicals} className="btn-secondary">Show All</button>
          </div>
          <div className="chemical-list">
            {chemicals.map((c) => (
              <div
                key={c.cas_number}
                className={`chemical-item ${selectedChemical?.cas_number === c.cas_number ? 'selected' : ''}`}
                onClick={() => selectChemical(c.cas_number)}
              >
                <strong>{c.name}</strong>
                <span className="chem-meta">
                  {c.formula && <span className="formula">{c.formula}</span>}
                  <span className="cas">{c.cas_number}</span>
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Scenario Configuration */}
        <div className="panel">
          <h2>Scenario Configuration</h2>
          {selectedChemical ? (
            <div className="selected-chem">
              <h3>{selectedChemical.name}</h3>
              <div className="chem-details">
                <span>MW: {selectedChemical.molecular_weight} g/mol</span>
                <span>State: {selectedChemical.state_at_ambient}</span>
                {selectedChemical.gas_density_ratio && (
                  <span>Density ratio: {selectedChemical.gas_density_ratio}</span>
                )}
              </div>
              <div className="thresholds">
                <h4>Exposure Thresholds (ppm)</h4>
                <table>
                  <tbody>
                    {selectedChemical.erpg_1_ppm && (
                      <tr><td className="zone-yellow">ERPG-1</td><td>{selectedChemical.erpg_1_ppm}</td></tr>
                    )}
                    {selectedChemical.erpg_2_ppm && (
                      <tr><td className="zone-orange">ERPG-2</td><td>{selectedChemical.erpg_2_ppm}</td></tr>
                    )}
                    {selectedChemical.erpg_3_ppm && (
                      <tr><td className="zone-red">ERPG-3</td><td>{selectedChemical.erpg_3_ppm}</td></tr>
                    )}
                    {selectedChemical.idlh_ppm && (
                      <tr><td className="zone-red">IDLH</td><td>{selectedChemical.idlh_ppm}</td></tr>
                    )}
                    {selectedChemical.aegl_1_60min_ppm && (
                      <tr><td className="zone-yellow">AEGL-1 (60min)</td><td>{selectedChemical.aegl_1_60min_ppm}</td></tr>
                    )}
                    {selectedChemical.aegl_2_60min_ppm && (
                      <tr><td className="zone-orange">AEGL-2 (60min)</td><td>{selectedChemical.aegl_2_60min_ppm}</td></tr>
                    )}
                    {selectedChemical.aegl_3_60min_ppm && (
                      <tr><td className="zone-red">AEGL-3 (60min)</td><td>{selectedChemical.aegl_3_60min_ppm}</td></tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            <p className="hint">← Select a chemical to start</p>
          )}

          <div className="scenario-form">
            <div className="form-row">
              <label>Scenario Type</label>
              <select value={scenarioType} onChange={(e) => setScenarioType(e.target.value)}>
                <option value="continuous">Continuous Release</option>
                <option value="instantaneous">Instantaneous Release</option>
              </select>
            </div>
            {scenarioType === 'continuous' ? (
              <div className="form-row">
                <label>Release Rate (kg/s)</label>
                <input type="number" value={releaseRate} onChange={(e) => setReleaseRate(Number(e.target.value))} min={0} step={0.1} />
              </div>
            ) : (
              <div className="form-row">
                <label>Total Release (kg)</label>
                <input type="number" value={totalRelease} onChange={(e) => setTotalRelease(Number(e.target.value))} min={0} />
              </div>
            )}
            <div className="form-row">
              <label>Release Height (m)</label>
              <input type="number" value={releaseHeight} onChange={(e) => setReleaseHeight(Number(e.target.value))} min={0} />
            </div>
            <h4>Weather Conditions</h4>
            <div className="form-row">
              <label>Stability Class</label>
              <select value={stabilityClass} onChange={(e) => setStabilityClass(e.target.value)}>
                <option value="A">A - Very Unstable</option>
                <option value="B">B - Unstable</option>
                <option value="C">C - Slightly Unstable</option>
                <option value="D">D - Neutral</option>
                <option value="E">E - Slightly Stable</option>
                <option value="F">F - Stable (Worst Case)</option>
              </select>
            </div>
            <div className="form-row">
              <label>Wind Speed (m/s)</label>
              <input type="number" value={windSpeed} onChange={(e) => setWindSpeed(Number(e.target.value))} min={0.1} step={0.5} />
            </div>
            <div className="form-row">
              <label>Wind Direction (°)</label>
              <input type="number" value={windDirection} onChange={(e) => setWindDirection(Number(e.target.value))} min={0} max={359} />
            </div>
            <button className="btn-calculate" onClick={calculateEPZ} disabled={!selectedChemical || loading}>
              {loading ? 'Calculating...' : '⚡ Calculate EPZ'}
            </button>
          </div>
        </div>

        {/* Results Panel */}
        <div className="panel results-panel">
          <h2>EPZ Results</h2>
          {calcResult ? (
            <div className="results">
              <div className="result-summary">
                <div className="summary-item">
                  <span className="label">Model</span>
                  <span className="value">{calcResult.model_description}</span>
                </div>
                <div className="summary-item">
                  <span className="label">Computation Time</span>
                  <span className="value">{calcResult.computation_time_ms.toFixed(1)} ms</span>
                </div>
                <div className="summary-item">
                  <span className="label">Total Affected Area</span>
                  <span className="value">{formatArea(calcResult.total_affected_area_km2)}</span>
                </div>
                <div className="summary-item">
                  <span className="label">Weather</span>
                  <span className="value">Stability {calcResult.stability_class}, Wind {windSpeed} m/s @ {windDirection}°</span>
                </div>
              </div>

              <h3>Zone Distances</h3>
              <table className="zone-table">
                <thead>
                  <tr>
                    <th>Zone</th>
                    <th>Threshold (ppm)</th>
                    <th>Downwind</th>
                    <th>Crosswind</th>
                    <th>Area</th>
                  </tr>
                </thead>
                <tbody>
                  {calcResult.zones.map((z, i) => (
                    <tr key={i}>
                      <td>
                        <span
                          className="zone-badge"
                          style={{ backgroundColor: zoneColors[z.threshold_name] || '#6b7280' }}
                        >
                          {z.threshold_name}
                        </span>
                      </td>
                      <td>{z.threshold_value_ppm?.toFixed(2) ?? 'N/A'}</td>
                      <td>{formatDistance(z.downwind_distance_m)}</td>
                      <td>{formatDistance(z.crosswind_width_m)}</td>
                      <td>{formatArea(z.area_km2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {/* Simple bar chart */}
              <h3>Zone Comparison</h3>
              <div className="bar-chart">
                {calcResult.zones.map((z, i) => {
                  const maxDist = Math.max(...calcResult.zones.map(zz => zz.downwind_distance_m ?? 0))
                  const pct = maxDist > 0 ? ((z.downwind_distance_m ?? 0) / maxDist) * 100 : 0
                  return (
                    <div key={i} className="bar-row">
                      <span className="bar-label">{z.threshold_name}</span>
                      <div className="bar-track">
                        <div
                          className="bar-fill"
                          style={{
                            width: `${pct}%`,
                            backgroundColor: zoneColors[z.threshold_name] || '#6b7280',
                          }}
                        />
                      </div>
                      <span className="bar-value">{formatDistance(z.downwind_distance_m)}</span>
                    </div>
                  )
                })}
              </div>

              {calcResult.warnings && calcResult.warnings.length > 0 && (
                <div className="warnings">
                  <h4>⚠️ Warnings</h4>
                  <ul>
                    {calcResult.warnings.map((w, i) => <li key={i}>{w}</li>)}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <p className="hint">Configure a scenario and click Calculate to see results</p>
          )}
        </div>
      </div>
    </div>
  )
}

export default App
