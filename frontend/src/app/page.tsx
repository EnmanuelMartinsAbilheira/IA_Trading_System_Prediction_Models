'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  TrendingUp, 
  TrendingDown, 
  Brain, 
  Play, 
  Pause, 
  RefreshCw,
  BarChart3,
  Settings,
  Activity
} from 'lucide-react'

export default function Home() {
  const [isSimulating, setIsSimulating] = useState(false)
  const [selectedModel, setSelectedModel] = useState('')
  const [predictionData, setPredictionData] = useState<any>(null)
  const [simulationData, setSimulationData] = useState<any>(null)
  const [testResults, setTestResults] = useState<any>(null)

  const mockTradingData = {
    portfolioValue: 12543.67,
    dailyChange: 2.34,
    dailyChangePercent: 0.19,
    activePositions: 5,
    winRate: 68.5,
    totalTrades: 142
  }

  const availableModels = [
    { id: 'lstm-v1', name: 'LSTM Model v1', accuracy: 0.87, status: 'active' },
    { id: 'transformer-v2', name: 'Transformer v2', accuracy: 0.92, status: 'training' },
    { id: 'ensemble-v1', name: 'Ensemble Model v1', accuracy: 0.89, status: 'active' }
  ]

  const handleRunPrediction = async () => {
    if (!selectedModel) return
    
    try {
      const response = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model: selectedModel })
      })
      const data = await response.json()
      setPredictionData(data)
    } catch (error) {
      console.error('Prediction error:', error)
    }
  }

  const toggleSimulation = () => {
    setIsSimulating(!isSimulating)
    if (!isSimulating) {
      // Start simulation
      setSimulationData({
        status: 'running',
        startTime: new Date(),
        trades: [],
        performance: { profit: 0, winRate: 0 }
      })
    }
  }

  const runComprehensiveTest = async () => {
    setTestResults(null)
    
    try {
      const response = await fetch('/api/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol: 'AAPL',
          models: availableModels.map(m => m.id),
          runs: 10,
          confidenceThreshold: 0.6
        })
      })
      
      const result = await response.json()
      if (result.success) {
        setTestResults(result.data)
      }
    } catch (error) {
      console.error('Test error:', error)
    }
  }

  return (
    <div className="min-h-screen bg-background p-4">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">AI Trading System</h1>
            <p className="text-muted-foreground">Advanced prediction models and trading simulator</p>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant={isSimulating ? "destructive" : "secondary"}>
              {isSimulating ? "Simulation Running" : "Simulation Stopped"}
            </Badge>
            <Button variant="outline" size="sm">
              <Settings className="h-4 w-4 mr-2" />
              Settings
            </Button>
          </div>
        </div>

        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Portfolio Value</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${mockTradingData.portfolioValue.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">
                +{mockTradingData.dailyChangePercent}% from yesterday
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Positions</CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{mockTradingData.activePositions}</div>
              <p className="text-xs text-muted-foreground">
                {mockTradingData.totalTrades} total trades
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Win Rate</CardTitle>
              <TrendingUp className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{mockTradingData.winRate}%</div>
              <Progress value={mockTradingData.winRate} className="mt-2" />
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Model Status</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">3 Active</div>
              <p className="text-xs text-muted-foreground">
                1 model training
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content Tabs */}
        <Tabs defaultValue="prediction" className="space-y-4">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="prediction">Prediction Models</TabsTrigger>
            <TabsTrigger value="simulator">Trading Simulator</TabsTrigger>
            <TabsTrigger value="testing">Model Testing</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </TabsList>

          <TabsContent value="prediction" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Brain className="h-5 w-5" />
                  AI Prediction Models
                </CardTitle>
                <CardDescription>
                  Select and run AI models for trading predictions
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {availableModels.map((model) => (
                    <Card key={model.id} className="cursor-pointer hover:shadow-md transition-shadow">
                      <CardHeader className="pb-3">
                        <div className="flex items-center justify-between">
                          <CardTitle className="text-sm">{model.name}</CardTitle>
                          <Badge variant={model.status === 'active' ? 'default' : 'secondary'}>
                            {model.status}
                          </Badge>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2">
                          <div className="flex justify-between text-sm">
                            <span>Accuracy:</span>
                            <span className="font-medium">{(model.accuracy * 100).toFixed(1)}%</span>
                          </div>
                          <Progress value={model.accuracy * 100} className="h-2" />
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>

                <div className="flex items-center gap-4 pt-4 border-t">
                  <div className="flex-1">
                    <Label htmlFor="model-select">Select Model</Label>
                    <Select value={selectedModel} onValueChange={setSelectedModel}>
                      <SelectTrigger>
                        <SelectValue placeholder="Choose a prediction model" />
                      </SelectTrigger>
                      <SelectContent>
                        {availableModels.map((model) => (
                          <SelectItem key={model.id} value={model.id}>
                            {model.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <Button onClick={handleRunPrediction} disabled={!selectedModel}>
                    <Brain className="h-4 w-4 mr-2" />
                    Run Prediction
                  </Button>
                </div>

                {predictionData && (
                  <Alert className="mt-4">
                    <AlertDescription>
                      <strong>Prediction Result:</strong> {JSON.stringify(predictionData, null, 2)}
                    </AlertDescription>
                  </Alert>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="simulator" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Play className="h-5 w-5" />
                  Trading Simulator
                </CardTitle>
                <CardDescription>
                  Simulate trading strategies with real-time data
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center gap-4">
                  <Button 
                    onClick={toggleSimulation}
                    variant={isSimulating ? "destructive" : "default"}
                  >
                    {isSimulating ? (
                      <>
                        <Pause className="h-4 w-4 mr-2" />
                        Stop Simulation
                      </>
                    ) : (
                      <>
                        <Play className="h-4 w-4 mr-2" />
                        Start Simulation
                      </>
                    )}
                  </Button>
                  <Button variant="outline">
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Reset Data
                  </Button>
                </div>

                {simulationData && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t">
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-sm">Simulation Status</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2">
                          <div className="flex justify-between">
                            <span>Status:</span>
                            <Badge variant="outline">{simulationData.status}</Badge>
                          </div>
                          <div className="flex justify-between">
                            <span>Start Time:</span>
                            <span className="text-sm">
                              {new Date(simulationData.startTime).toLocaleTimeString()}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span>Trades Executed:</span>
                            <span>{simulationData.trades.length}</span>
                          </div>
                        </div>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader>
                        <CardTitle className="text-sm">Performance</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2">
                          <div className="flex justify-between">
                            <span>Profit/Loss:</span>
                            <span className={`font-medium ${simulationData.performance.profit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                              ${simulationData.performance.profit.toFixed(2)}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span>Win Rate:</span>
                            <span>{simulationData.performance.winRate.toFixed(1)}%</span>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="testing" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Brain className="h-5 w-5" />
                  Model Testing Interface
                </CardTitle>
                <CardDescription>
                  Comprehensive testing and validation of AI prediction models
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Test Configuration */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-sm">Test Configuration</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div>
                        <Label htmlFor="test-symbol">Symbol</Label>
                        <Select defaultValue="AAPL">
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="AAPL">AAPL</SelectItem>
                            <SelectItem value="GOOGL">GOOGL</SelectItem>
                            <SelectItem value="MSFT">MSFT</SelectItem>
                            <SelectItem value="TSLA">TSLA</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div>
                        <Label htmlFor="test-models">Models to Test</Label>
                        <div className="space-y-2 mt-2">
                          {availableModels.map((model) => (
                            <div key={model.id} className="flex items-center space-x-2">
                              <input type="checkbox" id={model.id} defaultChecked />
                              <Label htmlFor={model.id} className="text-sm">
                                {model.name}
                              </Label>
                            </div>
                          ))}
                        </div>
                      </div>
                      <div>
                        <Label htmlFor="test-runs">Number of Runs</Label>
                        <Input type="number" defaultValue="10" min="1" max="100" />
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="text-sm">Test Parameters</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div>
                        <Label htmlFor="timeframe">Timeframe</Label>
                        <Select defaultValue="1h">
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="1m">1 Minute</SelectItem>
                            <SelectItem value="5m">5 Minutes</SelectItem>
                            <SelectItem value="1h">1 Hour</SelectItem>
                            <SelectItem value="1d">1 Day</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div>
                        <Label htmlFor="confidence-threshold">Confidence Threshold</Label>
                        <Input type="number" defaultValue="0.6" min="0" max="1" step="0.1" />
                      </div>
                      <div>
                        <Label htmlFor="test-duration">Test Duration (seconds)</Label>
                        <Input type="number" defaultValue="60" min="10" max="300" />
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="text-sm">Test Actions</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <Button className="w-full" onClick={runComprehensiveTest}>
                        <Brain className="h-4 w-4 mr-2" />
                        Run Test
                      </Button>
                      <Button variant="outline" className="w-full">
                        <RefreshCw className="h-4 w-4 mr-2" />
                        Reset Results
                      </Button>
                      <Button variant="outline" className="w-full">
                        Save Test Results
                      </Button>
                    </CardContent>
                  </Card>
                </div>

                {/* Test Results */}
                {testResults && (
                  <div className="space-y-4">
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg">Test Results Summary</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                          <div className="text-center">
                            <div className="text-2xl font-bold text-green-600">
                              {testResults.accuracy.toFixed(1)}%
                            </div>
                            <div className="text-sm text-muted-foreground">Overall Accuracy</div>
                          </div>
                          <div className="text-center">
                            <div className="text-2xl font-bold">{testResults.totalPredictions}</div>
                            <div className="text-sm text-muted-foreground">Total Predictions</div>
                          </div>
                          <div className="text-center">
                            <div className="text-2xl font-bold">{testResults.avgConfidence.toFixed(2)}</div>
                            <div className="text-sm text-muted-foreground">Avg Confidence</div>
                          </div>
                          <div className="text-center">
                            <div className="text-2xl font-bold">{testResults.executionTime}ms</div>
                            <div className="text-sm text-muted-foreground">Avg Execution Time</div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg">Model Performance</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-4">
                          {testResults.modelResults.map((result: any, index: number) => (
                            <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                              <div>
                                <div className="font-medium">{result.modelName}</div>
                                <div className="text-sm text-muted-foreground">
                                  {result.predictions} predictions
                                </div>
                              </div>
                              <div className="text-right">
                                <div className="font-bold">{result.accuracy.toFixed(1)}%</div>
                                <div className="text-sm text-muted-foreground">
                                  {result.avgConfidence.toFixed(2)} confidence
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg">Detailed Results</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="max-h-96 overflow-y-auto space-y-2">
                          {testResults.detailedResults.map((result: any, index: number) => (
                            <div key={index} className="p-3 border rounded-lg text-sm">
                              <div className="flex justify-between items-start mb-2">
                                <div>
                                  <span className="font-medium">{result.modelName}</span>
                                  <span className="ml-2 text-muted-foreground">on {result.symbol}</span>
                                </div>
                                <Badge variant={result.correct ? "default" : "secondary"}>
                                  {result.correct ? "Correct" : "Incorrect"}
                                </Badge>
                              </div>
                              <div className="grid grid-cols-2 gap-4 text-xs">
                                <div>
                                  <span className="text-muted-foreground">Predicted: </span>
                                  <span className={result.direction === 'up' ? 'text-green-600' : 'text-red-600'}>
                                    ${result.predictedPrice.toFixed(2)}
                                  </span>
                                </div>
                                <div>
                                  <span className="text-muted-foreground">Actual: </span>
                                  <span>${result.actualPrice.toFixed(2)}</span>
                                </div>
                                <div>
                                  <span className="text-muted-foreground">Confidence: </span>
                                  <span>{result.confidence.toFixed(2)}</span>
                                </div>
                                <div>
                                  <span className="text-muted-foreground">Error: </span>
                                  <span>{result.error.toFixed(2)}%</span>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="analytics" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Trading Analytics</CardTitle>
                <CardDescription>
                  Detailed performance metrics and analysis
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8 text-muted-foreground">
                  Analytics dashboard coming soon...
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}