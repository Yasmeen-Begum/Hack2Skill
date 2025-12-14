"""Insight Generator Agent for creating human-readable explanations and insights."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from weather_stock_dashboard.agents.base_agent import BaseWeatherStockAgent, BaseTool
from weather_stock_dashboard.services.correlation_service import correlation_service

logger = logging.getLogger(__name__)


class InsightGenerationTool(BaseTool):
    """Tool for generating insights from analysis results."""
    
    name: str = "insight_generation"
    description: str = "Generate human-readable insights from statistical analysis results"
    
    def _run(self, analysis_type: str, results: Dict[str, Any]) -> str:
        """Generate insights from analysis results."""
        try:
            agent = InsightGeneratorAgent()
            insight = agent._generate_insight_text(analysis_type, results)
            return insight
        except Exception as e:
            return f"Insight generation failed: {str(e)}"


class ExplanationTool(BaseTool):
    """Tool for generating explanations of methodology and limitations."""
    
    name: str = "explanation_generation"
    description: str = "Generate explanations of analysis methodology and limitations"
    
    def _run(self, analysis_type: str, methodology: Dict[str, Any]) -> str:
        """Generate methodology explanation."""
        try:
            agent = InsightGeneratorAgent()
            explanation = agent._generate_methodology_explanation(analysis_type, methodology)
            return explanation
        except Exception as e:
            return f"Explanation generation failed: {str(e)}"


class SignificanceTool(BaseTool):
    """Tool for interpreting statistical significance."""
    
    name: str = "significance_interpretation"
    description: str = "Interpret statistical significance and confidence levels"
    
    def _run(self, p_value: float, confidence_level: float, test_type: str) -> str:
        """Interpret statistical significance."""
        try:
            agent = InsightGeneratorAgent()
            interpretation = agent._interpret_statistical_significance(p_value, confidence_level, test_type)
            return interpretation
        except Exception as e:
            return f"Significance interpretation failed: {str(e)}"


class InsightGeneratorAgent(BaseWeatherStockAgent):
    """Agent for generating human-readable insights and explanations."""
    
    def __init__(self):
        """Initialize Insight Generator Agent."""
        super().__init__(
            name="insight_generator",
            role="Data Insights Analyst",
            goal="Generate clear, actionable insights from complex statistical analyses and explain methodologies",
            backstory="""You are an expert data storyteller with the ability to translate 
            complex statistical analyses into clear, actionable business insights. You 
            specialize in explaining weather-stock correlations, time series patterns, 
            and volatility analysis in terms that both technical and non-technical 
            stakeholders can understand."""
        )
        
        self.insight_templates = {
            "correlation": "Weather-stock correlation analysis",
            "volatility": "Volatility analysis insights",
            "forecast": "Time series forecast interpretation",
            "validation": "Data quality assessment"
        }
        
    def get_tools(self) -> List[BaseTool]:
        """Get tools for insight generation."""
        return [
            InsightGenerationTool(),
            ExplanationTool(),
            SignificanceTool()
        ]
    
    async def execute_task(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute insight generation task."""
        try:
            task_type = context.get("task_type", "generate_insights")
            analysis_results = context.get("analysis_results", {})
            analysis_type = context.get("analysis_type", "general")
            
            if task_type == "generate_insights":
                result = await self._generate_comprehensive_insights(analysis_results, analysis_type, context)
            
            elif task_type == "explain_methodology":
                result = await self._explain_analysis_methodology(analysis_results, analysis_type)
            
            elif task_type == "interpret_significance":
                result = await self._interpret_statistical_results(analysis_results, context)
            
            elif task_type == "create_summary":
                result = await self._create_executive_summary(analysis_results, analysis_type, context)
            
            elif task_type == "generate_recommendations":
                result = await self._generate_actionable_recommendations(analysis_results, analysis_type, context)
            
            else:
                raise ValueError(f"Unknown task type: {task_type}")
            
            # Update agent memory
            self.update_memory(f"last_{task_type}_result", result)
            
            return {
                "agent": self.name,
                "task": task_description,
                "result": result,
                "timestamp": datetime.utcnow().isoformat(),
                "summary": result.get("summary", "Insight generation completed successfully")
            }
            
        except Exception as e:
            logger.error(f"Insight generation task failed: {e}")
            return {
                "agent": self.name,
                "task": task_description,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "summary": f"Insight generation failed: {str(e)}"
            }
    
    async def _generate_comprehensive_insights(self, analysis_results: Dict[str, Any], 
                                             analysis_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive insights from analysis results."""
        try:
            insights = []
            
            # Generate main insight
            main_insight = self._generate_insight_text(analysis_type, analysis_results)
            insights.append({
                "type": "main",
                "content": main_insight,
                "confidence": self._assess_insight_confidence(analysis_results)
            })
            
            # Generate supporting insights
            supporting_insights = self._generate_supporting_insights(analysis_results, analysis_type)
            insights.extend(supporting_insights)
            
            # Generate implications
            implications = self._generate_implications(analysis_results, analysis_type, context)
            
            # Generate limitations
            limitations = self._identify_analysis_limitations(analysis_results, analysis_type)
            
            return {
                "analysis_type": analysis_type,
                "insights": insights,
                "implications": implications,
                "limitations": limitations,
                "confidence_assessment": self._assess_overall_confidence(analysis_results),
                "summary": f"Generated {len(insights)} insights for {analysis_type} analysis"
            }
            
        except Exception as e:
            logger.error(f"Comprehensive insight generation failed: {e}")
            raise
    
    async def _explain_analysis_methodology(self, analysis_results: Dict[str, Any], 
                                          analysis_type: str) -> Dict[str, Any]:
        """Explain the methodology used in the analysis."""
        try:
            methodology_explanation = self._generate_methodology_explanation(analysis_type, analysis_results)
            
            # Extract key parameters
            key_parameters = self._extract_key_parameters(analysis_results, analysis_type)
            
            # Explain assumptions
            assumptions = self._explain_assumptions(analysis_type)
            
            # Explain interpretation guidelines
            interpretation_guide = self._create_interpretation_guide(analysis_type)
            
            return {
                "analysis_type": analysis_type,
                "methodology_explanation": methodology_explanation,
                "key_parameters": key_parameters,
                "assumptions": assumptions,
                "interpretation_guide": interpretation_guide,
                "summary": f"Methodology explanation generated for {analysis_type} analysis"
            }
            
        except Exception as e:
            logger.error(f"Methodology explanation failed: {e}")
            raise
    
    async def _interpret_statistical_results(self, analysis_results: Dict[str, Any], 
                                           context: Dict[str, Any]) -> Dict[str, Any]:
        """Interpret statistical significance and confidence levels."""
        try:
            interpretations = []
            
            # Look for statistical measures in results
            if "p_value" in analysis_results:
                p_value = analysis_results["p_value"]
                test_type = context.get("test_type", "correlation")
                interpretation = self._interpret_statistical_significance(p_value, 0.95, test_type)
                interpretations.append({
                    "measure": "p_value",
                    "value": p_value,
                    "interpretation": interpretation
                })
            
            if "confidence_level" in analysis_results:
                confidence = analysis_results["confidence_level"]
                interpretations.append({
                    "measure": "confidence_level",
                    "value": confidence,
                    "interpretation": self._interpret_confidence_level(confidence)
                })
            
            if "correlation_coefficient" in analysis_results:
                correlation = analysis_results["correlation_coefficient"]
                interpretations.append({
                    "measure": "correlation_coefficient",
                    "value": correlation,
                    "interpretation": self._interpret_correlation_strength(correlation)
                })
            
            return {
                "statistical_interpretations": interpretations,
                "overall_significance": self._assess_overall_significance(interpretations),
                "summary": f"Interpreted {len(interpretations)} statistical measures"
            }
            
        except Exception as e:
            logger.error(f"Statistical interpretation failed: {e}")
            raise
    
    async def _create_executive_summary(self, analysis_results: Dict[str, Any], 
                                      analysis_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create executive summary of analysis."""
        try:
            # Key findings
            key_findings = self._extract_key_findings(analysis_results, analysis_type)
            
            # Business implications
            business_implications = self._generate_business_implications(analysis_results, analysis_type, context)
            
            # Action items
            action_items = self._generate_action_items(analysis_results, analysis_type, context)
            
            # Risk assessment
            risk_assessment = self._assess_risks(analysis_results, analysis_type)
            
            # Executive summary text
            summary_text = self._create_summary_text(key_findings, business_implications, action_items)
            
            return {
                "executive_summary": summary_text,
                "key_findings": key_findings,
                "business_implications": business_implications,
                "action_items": action_items,
                "risk_assessment": risk_assessment,
                "summary": "Executive summary created successfully"
            }
            
        except Exception as e:
            logger.error(f"Executive summary creation failed: {e}")
            raise
    
    async def _generate_actionable_recommendations(self, analysis_results: Dict[str, Any], 
                                                 analysis_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate actionable recommendations based on analysis."""
        try:
            recommendations = []
            
            # Analysis-specific recommendations
            if analysis_type == "correlation":
                recommendations.extend(self._generate_correlation_recommendations(analysis_results))
            elif analysis_type == "volatility":
                recommendations.extend(self._generate_volatility_recommendations(analysis_results))
            elif analysis_type == "forecast":
                recommendations.extend(self._generate_forecast_recommendations(analysis_results))
            
            # General recommendations
            recommendations.extend(self._generate_general_recommendations(analysis_results, context))
            
            # Prioritize recommendations
            prioritized_recommendations = self._prioritize_recommendations(recommendations, analysis_results)
            
            return {
                "recommendations": prioritized_recommendations,
                "implementation_timeline": self._suggest_implementation_timeline(prioritized_recommendations),
                "success_metrics": self._suggest_success_metrics(analysis_type, prioritized_recommendations),
                "summary": f"Generated {len(prioritized_recommendations)} actionable recommendations"
            }
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            raise
    
    def _generate_insight_text(self, analysis_type: str, results: Dict[str, Any]) -> str:
        """Generate main insight text based on analysis type."""
        if analysis_type == "correlation":
            return self._generate_correlation_insight(results)
        elif analysis_type == "volatility":
            return self._generate_volatility_insight(results)
        elif analysis_type == "forecast":
            return self._generate_forecast_insight(results)
        elif analysis_type == "validation":
            return self._generate_validation_insight(results)
        else:
            return f"Analysis of {analysis_type} completed with notable patterns identified."
    
    def _generate_correlation_insight(self, results: Dict[str, Any]) -> str:
        """Generate insight for correlation analysis."""
        correlation = results.get("simple_correlation", 0)
        weather_var = results.get("weather_variable", "weather")
        stock_var = results.get("stock_variable", "stock")
        
        if abs(correlation) > 0.5:
            strength = "strong"
        elif abs(correlation) > 0.3:
            strength = "moderate"
        elif abs(correlation) > 0.1:
            strength = "weak"
        else:
            strength = "negligible"
        
        direction = "positive" if correlation > 0 else "negative"
        
        insight = f"Analysis reveals a {strength} {direction} correlation (r={correlation:.3f}) between {weather_var} and {stock_var}. "
        
        # Add context about significance
        if results.get("correlation_significance", {}).get("is_significant", False):
            insight += "This relationship is statistically significant, suggesting a meaningful connection between weather patterns and market performance."
        else:
            insight += "While this pattern exists in the data, it may not be statistically significant and should be interpreted with caution."
        
        return insight
    
    def _generate_volatility_insight(self, results: Dict[str, Any]) -> str:
        """Generate insight for volatility analysis."""
        if "garch_analysis" in results:
            garch_results = results["garch_analysis"]
            best_model = garch_results["best_model"]["name"]
            vol_stats = garch_results["volatility_statistics"]
            clustering = garch_results["volatility_clustering"]
            
            insight = f"Volatility analysis using {best_model} model shows "
            
            mean_vol = vol_stats["mean_volatility"]
            if mean_vol > 0.03:
                insight += "elevated volatility levels "
            elif mean_vol > 0.015:
                insight += "moderate volatility levels "
            else:
                insight += "low volatility levels "
            
            insight += f"with {clustering['interpretation'].lower()}. "
            
            if clustering["clustering_score"] > 0.5:
                insight += "This suggests that periods of high volatility tend to be followed by more high volatility, creating predictable patterns for risk management."
            
            return insight
        
        return "Volatility analysis completed with patterns identified in market behavior."
    
    def _generate_forecast_insight(self, results: Dict[str, Any]) -> str:
        """Generate insight for forecast analysis."""
        if "forecast" in results and "arima_order" in results:
            forecast = results["forecast"]
            order = results["arima_order"]
            
            if len(forecast) >= 2:
                if forecast[-1] > forecast[0]:
                    trend = "upward"
                elif forecast[-1] < forecast[0]:
                    trend = "downward"
                else:
                    trend = "stable"
            else:
                trend = "stable"
            
            insight = f"Time series forecast using ARIMA{order} model predicts a {trend} trend over the next {len(forecast)} periods. "
            
            # Add confidence assessment
            if results.get("model_quality", {}).get("aic", float('inf')) < 1000:
                insight += "The model shows good fit to historical data, providing reliable forecasts."
            else:
                insight += "Forecast should be interpreted with caution due to model limitations."
            
            return insight
        
        return "Time series forecast generated with trend analysis completed."
    
    def _generate_validation_insight(self, results: Dict[str, Any]) -> str:
        """Generate insight for data validation."""
        if "validity_rate" in results:
            validity_rate = results["validity_rate"]
            total_records = results.get("total_records", 0)
            
            if validity_rate >= 0.95:
                quality = "excellent"
            elif validity_rate >= 0.85:
                quality = "good"
            elif validity_rate >= 0.70:
                quality = "fair"
            else:
                quality = "poor"
            
            insight = f"Data quality assessment of {total_records} records shows {quality} quality with {validity_rate:.1%} validity rate. "
            
            issues = results.get("issues", [])
            if issues:
                insight += f"Key issues identified: {len(issues)} data quality concerns that should be addressed before analysis."
            else:
                insight += "No significant data quality issues detected."
            
            return insight
        
        return "Data validation completed with quality assessment performed."
    
    def _generate_supporting_insights(self, results: Dict[str, Any], analysis_type: str) -> List[Dict[str, Any]]:
        """Generate supporting insights."""
        supporting = []
        
        # Look for additional patterns in results
        if "cross_correlation" in results:
            cross_corr = results["cross_correlation"]
            optimal_lag = cross_corr.get("optimal_lag", 0)
            if optimal_lag > 0:
                supporting.append({
                    "type": "temporal",
                    "content": f"Optimal correlation occurs with a {optimal_lag}-period lag, suggesting delayed market response to weather changes.",
                    "confidence": "medium"
                })
        
        if "granger_causality" in results:
            granger = results["granger_causality"]
            if granger.get("is_causal", False):
                supporting.append({
                    "type": "causality",
                    "content": f"Granger causality test suggests weather patterns may help predict market movements (p={granger.get('min_p_value', 1.0):.3f}).",
                    "confidence": "high" if granger.get('min_p_value', 1.0) < 0.01 else "medium"
                })
        
        return supporting
    
    def _generate_implications(self, results: Dict[str, Any], analysis_type: str, context: Dict[str, Any]) -> List[str]:
        """Generate implications of the analysis."""
        implications = []
        
        if analysis_type == "correlation":
            correlation = results.get("simple_correlation", 0)
            if abs(correlation) > 0.3:
                implications.append("Weather patterns may be a useful factor in market analysis and prediction models")
                implications.append("Portfolio diversification strategies could consider weather-sensitive sectors")
            
        elif analysis_type == "volatility":
            if "volatility_clustering" in results.get("garch_analysis", {}):
                clustering = results["garch_analysis"]["volatility_clustering"]
                if clustering.get("clustering_score", 0) > 0.5:
                    implications.append("Volatility clustering suggests risk management strategies should account for persistent volatility periods")
                    implications.append("Options pricing and hedging strategies may benefit from volatility forecasting")
        
        elif analysis_type == "forecast":
            if "forecast" in results:
                implications.append("Time series patterns provide basis for short-term market predictions")
                implications.append("Forecast uncertainty should be incorporated into trading and investment decisions")
        
        return implications
    
    def _identify_analysis_limitations(self, results: Dict[str, Any], analysis_type: str) -> List[str]:
        """Identify limitations of the analysis."""
        limitations = []
        
        # Data-related limitations
        data_points = results.get("data_points", 0)
        if data_points < 100:
            limitations.append("Limited sample size may affect reliability of results")
        
        # Analysis-specific limitations
        if analysis_type == "correlation":
            limitations.append("Correlation does not imply causation - relationships may be spurious")
            limitations.append("External factors not considered may influence both weather and market variables")
        
        elif analysis_type == "volatility":
            limitations.append("GARCH models assume specific volatility dynamics that may not hold in all market conditions")
            limitations.append("Model parameters may change over time, affecting forecast accuracy")
        
        elif analysis_type == "forecast":
            limitations.append("Time series forecasts assume historical patterns will continue")
            limitations.append("Forecast accuracy decreases with longer prediction horizons")
        
        # General limitations
        limitations.append("Results are based on historical data and may not reflect future market conditions")
        
        return limitations
    
    def _assess_insight_confidence(self, results: Dict[str, Any]) -> str:
        """Assess confidence level of insights."""
        confidence_factors = []
        
        # Statistical significance
        if results.get("correlation_significance", {}).get("is_significant", False):
            confidence_factors.append("significant")
        
        # Sample size
        data_points = results.get("data_points", 0)
        if data_points > 200:
            confidence_factors.append("large_sample")
        elif data_points > 50:
            confidence_factors.append("adequate_sample")
        
        # Model quality
        if "model_quality" in results:
            aic = results["model_quality"].get("aic", float('inf'))
            if aic < 500:
                confidence_factors.append("good_model")
        
        if len(confidence_factors) >= 2:
            return "high"
        elif len(confidence_factors) == 1:
            return "medium"
        else:
            return "low"
    
    def _assess_overall_confidence(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall confidence in analysis results."""
        confidence_score = 0
        factors = []
        
        # Check various confidence indicators
        if results.get("correlation_significance", {}).get("is_significant", False):
            confidence_score += 2
            factors.append("Statistical significance confirmed")
        
        data_points = results.get("data_points", 0)
        if data_points > 100:
            confidence_score += 1
            factors.append("Adequate sample size")
        
        if "model_quality" in results:
            aic = results["model_quality"].get("aic", float('inf'))
            if aic < 1000:
                confidence_score += 1
                factors.append("Good model fit")
        
        # Overall assessment
        if confidence_score >= 3:
            level = "High"
        elif confidence_score >= 2:
            level = "Medium"
        else:
            level = "Low"
        
        return {
            "level": level,
            "score": confidence_score,
            "supporting_factors": factors
        }
    
    def _generate_methodology_explanation(self, analysis_type: str, results: Dict[str, Any]) -> str:
        """Generate explanation of analysis methodology."""
        if analysis_type == "correlation":
            return """Correlation analysis examines the linear relationship between weather variables and stock market performance. 
            The analysis uses Pearson correlation coefficients to measure association strength, cross-correlation to identify 
            optimal time lags, and Granger causality tests to assess predictive relationships. Statistical significance 
            is evaluated using t-tests with appropriate degrees of freedom."""
        
        elif analysis_type == "volatility":
            return """Volatility analysis employs GARCH (Generalized Autoregressive Conditional Heteroskedasticity) models 
            to capture time-varying volatility in stock returns. The methodology includes model selection based on 
            information criteria (AIC/BIC), volatility clustering detection, and regime analysis. Different GARCH 
            variants (standard, EGARCH, GJR-GARCH) are compared to identify the best-fitting model."""
        
        elif analysis_type == "forecast":
            return """Time series forecasting uses ARIMA (AutoRegressive Integrated Moving Average) models to predict 
            future values based on historical patterns. The methodology includes stationarity testing, automatic 
            parameter selection using information criteria, and forecast generation with confidence intervals. 
            Model diagnostics ensure residuals are well-behaved and assumptions are met."""
        
        else:
            return f"The {analysis_type} analysis follows established statistical methodologies with appropriate validation and testing procedures."
    
    def _extract_key_parameters(self, results: Dict[str, Any], analysis_type: str) -> Dict[str, Any]:
        """Extract key parameters from analysis results."""
        parameters = {}
        
        if analysis_type == "correlation":
            parameters["correlation_coefficient"] = results.get("simple_correlation", 0)
            parameters["sample_size"] = results.get("data_points", 0)
            if "cross_correlation" in results:
                parameters["optimal_lag"] = results["cross_correlation"].get("optimal_lag", 0)
        
        elif analysis_type == "volatility":
            if "garch_analysis" in results:
                garch = results["garch_analysis"]
                parameters["best_model"] = garch["best_model"]["name"]
                parameters["mean_volatility"] = garch["volatility_statistics"]["mean_volatility"]
                parameters["clustering_score"] = garch["volatility_clustering"]["clustering_score"]
        
        elif analysis_type == "forecast":
            parameters["arima_order"] = results.get("arima_order", (0, 0, 0))
            parameters["forecast_horizon"] = results.get("forecast_horizon", 0)
            if "model_quality" in results:
                parameters["aic"] = results["model_quality"]["aic"]
        
        return parameters
    
    def _explain_assumptions(self, analysis_type: str) -> List[str]:
        """Explain key assumptions of the analysis."""
        if analysis_type == "correlation":
            return [
                "Linear relationship between variables",
                "Normal distribution of residuals",
                "Independence of observations",
                "Stationarity of time series"
            ]
        elif analysis_type == "volatility":
            return [
                "Volatility clustering in financial returns",
                "Conditional heteroskedasticity",
                "Stationarity of return series",
                "Specific GARCH model structure"
            ]
        elif analysis_type == "forecast":
            return [
                "Stationarity of differenced series",
                "Linear relationships in ARIMA structure",
                "Constant parameters over time",
                "Normal distribution of innovations"
            ]
        else:
            return ["Standard statistical assumptions apply"]
    
    def _create_interpretation_guide(self, analysis_type: str) -> Dict[str, str]:
        """Create guide for interpreting results."""
        if analysis_type == "correlation":
            return {
                "correlation_strength": "0.0-0.3: weak, 0.3-0.7: moderate, 0.7-1.0: strong",
                "p_value": "<0.05: significant, <0.01: highly significant",
                "confidence_level": ">0.95: high confidence, 0.90-0.95: moderate confidence"
            }
        elif analysis_type == "volatility":
            return {
                "volatility_level": "<0.01: low, 0.01-0.03: moderate, >0.03: high",
                "clustering_score": "<0.3: weak, 0.3-0.7: moderate, >0.7: strong clustering",
                "model_selection": "Lower AIC/BIC indicates better model fit"
            }
        elif analysis_type == "forecast":
            return {
                "forecast_accuracy": "Lower AIC indicates better model fit",
                "confidence_intervals": "Wider intervals indicate higher uncertainty",
                "residual_tests": "p>0.05 indicates good model specification"
            }
        else:
            return {"general": "Refer to standard statistical interpretation guidelines"}
    
    def _interpret_statistical_significance(self, p_value: float, confidence_level: float, test_type: str) -> str:
        """Interpret statistical significance."""
        alpha = 1 - confidence_level
        
        if p_value < 0.001:
            return f"Highly significant result (p<0.001) - very strong evidence against null hypothesis in {test_type} test"
        elif p_value < 0.01:
            return f"Significant result (p<0.01) - strong evidence against null hypothesis in {test_type} test"
        elif p_value < alpha:
            return f"Significant result (p<{alpha}) - evidence against null hypothesis in {test_type} test"
        else:
            return f"Not significant (p={p_value:.3f}) - insufficient evidence against null hypothesis in {test_type} test"
    
    def _interpret_confidence_level(self, confidence: float) -> str:
        """Interpret confidence level."""
        if confidence >= 0.99:
            return "Very high confidence (99%+) - results are highly reliable"
        elif confidence >= 0.95:
            return "High confidence (95%+) - results are reliable"
        elif confidence >= 0.90:
            return "Moderate confidence (90%+) - results should be interpreted with some caution"
        else:
            return f"Low confidence ({confidence:.1%}) - results should be interpreted with significant caution"
    
    def _interpret_correlation_strength(self, correlation: float) -> str:
        """Interpret correlation coefficient strength."""
        abs_corr = abs(correlation)
        direction = "positive" if correlation > 0 else "negative"
        
        if abs_corr >= 0.7:
            strength = "strong"
        elif abs_corr >= 0.3:
            strength = "moderate"
        elif abs_corr >= 0.1:
            strength = "weak"
        else:
            strength = "negligible"
        
        return f"{strength.capitalize()} {direction} correlation (r={correlation:.3f})"
    
    def _extract_key_findings(self, results: Dict[str, Any], analysis_type: str) -> List[str]:
        """Extract key findings from analysis results."""
        findings = []
        
        if analysis_type == "correlation":
            correlation = results.get("simple_correlation", 0)
            findings.append(f"Correlation coefficient: {correlation:.3f}")
            
            if results.get("correlation_significance", {}).get("is_significant", False):
                findings.append("Statistically significant relationship identified")
            
            if "cross_correlation" in results:
                optimal_lag = results["cross_correlation"]["optimal_lag"]
                findings.append(f"Optimal correlation at {optimal_lag}-period lag")
        
        elif analysis_type == "volatility":
            if "garch_analysis" in results:
                garch = results["garch_analysis"]
                findings.append(f"Best volatility model: {garch['best_model']['name']}")
                findings.append(f"Volatility clustering: {garch['volatility_clustering']['interpretation']}")
        
        return findings
    
    def _generate_business_implications(self, results: Dict[str, Any], analysis_type: str, context: Dict[str, Any]) -> List[str]:
        """Generate business implications."""
        implications = []
        
        if analysis_type == "correlation":
            correlation = abs(results.get("simple_correlation", 0))
            if correlation > 0.3:
                implications.append("Weather data could enhance trading and investment models")
                implications.append("Sector allocation strategies may benefit from weather considerations")
        
        elif analysis_type == "volatility":
            implications.append("Risk management strategies should account for volatility patterns")
            implications.append("Options and derivatives pricing may benefit from volatility forecasting")
        
        return implications
    
    def _generate_action_items(self, results: Dict[str, Any], analysis_type: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate specific action items."""
        actions = []
        
        if analysis_type == "correlation":
            correlation = abs(results.get("simple_correlation", 0))
            if correlation > 0.3:
                actions.append({
                    "action": "Integrate weather data into trading models",
                    "priority": "high",
                    "timeline": "3-6 months"
                })
        
        elif analysis_type == "volatility":
            actions.append({
                "action": "Implement volatility-based risk controls",
                "priority": "medium",
                "timeline": "1-3 months"
            })
        
        return actions
    
    def _assess_risks(self, results: Dict[str, Any], analysis_type: str) -> Dict[str, Any]:
        """Assess risks associated with the analysis."""
        risks = []
        
        # Data quality risks
        data_points = results.get("data_points", 0)
        if data_points < 100:
            risks.append("Limited data may lead to unreliable conclusions")
        
        # Model risks
        if analysis_type == "forecast":
            risks.append("Forecast accuracy may degrade over time")
        
        risk_level = "high" if len(risks) > 2 else "medium" if len(risks) > 0 else "low"
        
        return {
            "level": risk_level,
            "identified_risks": risks,
            "mitigation_strategies": ["Regular model validation", "Continuous data quality monitoring"]
        }
    
    def _create_summary_text(self, key_findings: List[str], implications: List[str], actions: List[Dict[str, Any]]) -> str:
        """Create executive summary text."""
        summary = "Executive Summary:\n\n"
        
        if key_findings:
            summary += "Key Findings:\n"
            for finding in key_findings[:3]:  # Top 3 findings
                summary += f"• {finding}\n"
            summary += "\n"
        
        if implications:
            summary += "Business Implications:\n"
            for implication in implications[:2]:  # Top 2 implications
                summary += f"• {implication}\n"
            summary += "\n"
        
        if actions:
            summary += "Recommended Actions:\n"
            for action in actions[:2]:  # Top 2 actions
                summary += f"• {action['action']} (Priority: {action['priority']})\n"
        
        return summary
    
    def _generate_correlation_recommendations(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate correlation-specific recommendations."""
        recommendations = []
        
        correlation = abs(results.get("simple_correlation", 0))
        if correlation > 0.3:
            recommendations.append({
                "recommendation": "Consider weather factors in portfolio construction",
                "rationale": "Significant correlation suggests weather impacts market performance",
                "priority": "high"
            })
        
        return recommendations
    
    def _generate_volatility_recommendations(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate volatility-specific recommendations."""
        recommendations = []
        
        if "garch_analysis" in results:
            clustering_score = results["garch_analysis"]["volatility_clustering"]["clustering_score"]
            if clustering_score > 0.5:
                recommendations.append({
                    "recommendation": "Implement dynamic hedging strategies",
                    "rationale": "Strong volatility clustering enables predictive risk management",
                    "priority": "medium"
                })
        
        return recommendations
    
    def _generate_forecast_recommendations(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate forecast-specific recommendations."""
        recommendations = []
        
        if "model_quality" in results:
            aic = results["model_quality"].get("aic", float('inf'))
            if aic < 1000:
                recommendations.append({
                    "recommendation": "Use forecasts for short-term planning",
                    "rationale": "Good model fit supports reliable short-term predictions",
                    "priority": "medium"
                })
        
        return recommendations
    
    def _generate_general_recommendations(self, results: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate general recommendations."""
        return [
            {
                "recommendation": "Continue monitoring and validation",
                "rationale": "Regular validation ensures continued model reliability",
                "priority": "low"
            }
        ]
    
    def _prioritize_recommendations(self, recommendations: List[Dict[str, Any]], results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prioritize recommendations based on analysis results."""
        # Sort by priority: high > medium > low
        priority_order = {"high": 3, "medium": 2, "low": 1}
        return sorted(recommendations, key=lambda x: priority_order.get(x["priority"], 0), reverse=True)
    
    def _suggest_implementation_timeline(self, recommendations: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Suggest implementation timeline for recommendations."""
        timeline = {
            "immediate": [],
            "short_term": [],
            "medium_term": [],
            "long_term": []
        }
        
        for rec in recommendations:
            if rec["priority"] == "high":
                timeline["short_term"].append(rec["recommendation"])
            elif rec["priority"] == "medium":
                timeline["medium_term"].append(rec["recommendation"])
            else:
                timeline["long_term"].append(rec["recommendation"])
        
        return timeline
    
    def _suggest_success_metrics(self, analysis_type: str, recommendations: List[Dict[str, Any]]) -> List[str]:
        """Suggest metrics to measure success of recommendations."""
        metrics = []
        
        if analysis_type == "correlation":
            metrics.append("Improvement in prediction accuracy")
            metrics.append("Reduction in portfolio volatility")
        elif analysis_type == "volatility":
            metrics.append("Better risk-adjusted returns")
            metrics.append("Reduced maximum drawdown")
        elif analysis_type == "forecast":
            metrics.append("Forecast accuracy over time")
            metrics.append("Decision-making improvement")
        
        return metrics
    
    def _assess_overall_significance(self, interpretations: List[Dict[str, Any]]) -> str:
        """Assess overall statistical significance."""
        significant_count = sum(1 for interp in interpretations 
                              if "significant" in interp.get("interpretation", "").lower())
        
        if significant_count >= len(interpretations) * 0.7:
            return "Highly significant results across multiple measures"
        elif significant_count >= len(interpretations) * 0.5:
            return "Moderately significant results"
        else:
            return "Limited statistical significance"