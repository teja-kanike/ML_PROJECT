{% extends "base.html" %}

{% block title %}ML Insights - Hostel Management System{% endblock %}

{% block content %}
<div class="container-fluid py-4">
    <div class="row mb-4">
        <div class="col">
            <div class="dashboard-card">
                <h2 class="mb-4">
                    <i class="fas fa-brain me-2"></i>Machine Learning Insights
                </h2>
                <p class="text-muted">Advanced AI analytics and predictions</p>
            </div>
        </div>
    </div>

    <!-- ML Models Status -->
    <div class="row mb-4">
        <div class="col">
            <div class="dashboard-card">
                <h4 class="mb-4">ML Models Status</h4>
                <div class="row">
                    <div class="col-md-4">
                        <div class="card {{ 'bg-success' if ml_models_info.sentiment_analyzer else 'bg-danger' }} text-white mb-3">
                            <div class="card-body text-center">
                                <i class="fas fa-comment-dots fa-2x mb-2"></i>
                                <h5>Sentiment Analyzer</h5>
                                <span class="badge bg-{{ 'light' if ml_models_info.sentiment_analyzer else 'warning' }} text-dark">
                                    {{ 'Trained' if ml_models_info.sentiment_analyzer else 'Not Trained' }}
                                </span>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card {{ 'bg-success' if ml_models_info.occupancy_predictor else 'bg-danger' }} text-white mb-3">
                            <div class="card-body text-center">
                                <i class="fas fa-chart-line fa-2x mb-2"></i>
                                <h5>Occupancy Predictor</h5>
                                <span class="badge bg-{{ 'light' if ml_models_info.occupancy_predictor else 'warning' }} text-dark">
                                    {{ 'Trained' if ml_models_info.occupancy_predictor else 'Not Trained' }}
                                </span>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card {{ 'bg-success' if ml_models_info.complaint_classifier else 'bg-danger' }} text-white mb-3">
                            <div class="card-body text-center">
                                <i class="fas fa-exclamation-triangle fa-2x mb-2"></i>
                                <h5>Complaint Classifier</h5>
                                <span class="badge bg-{{ 'light' if ml_models_info.complaint_classifier else 'warning' }} text-dark">
                                    {{ 'Trained' if ml_models_info.complaint_classifier else 'Not Trained' }}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Occupancy Predictions -->
    <div class="row mb-4">
        <div class="col">
            <div class="dashboard-card">
                <h4 class="mb-4">Occupancy Predictions (Next 30 Days)</h4>
                {% if occupancy_trend %}
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead class="table-dark">
                            <tr>
                                <th>Date</th>
                                <th>Predicted Occupancy</th>
                                <th>Trend</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for day in occupancy_trend %}
                            <tr>
                                <td>{{ day.date }}</td>
                                <td>
                                    <div class="progress">
                                        <div class="progress-bar bg-{{ 'success' if day.occupancy_rate < 70 else 'warning' if day.occupancy_rate < 90 else 'danger' }}" 
                                             style="width: {{ day.occupancy_rate }}%">
                                            {{ "%.1f"|format(day.occupancy_rate) }}%
                                        </div>
                                    </div>
                                </td>
                                <td>
                                    <i class="fas fa-arrow-{{ 'up' if day.occupancy_rate > 70 else 'down' }} text-{{ 'success' if day.occupancy_rate > 70 else 'danger' }}"></i>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% else %}
                <p class="text-muted">No occupancy data available</p>
                {% endif %}
            </div>
        </div>
    </div>

    <!-- Complaint Statistics -->
    <div class="row">
        <div class="col-md-6">
            <div class="dashboard-card">
                <h4 class="mb-4">Complaint Categories</h4>
                {% if complaint_stats %}
                <div class="list-group">
                    {% for stat in complaint_stats %}
                    <div class="list-group-item">
                        <div class="d-flex justify-content-between align-items-center">
                            <span>
                                <strong>{{ stat[0]|title }}</strong> - {{ stat[1]|title }} Priority
                            </span>
                            <span class="badge bg-primary">{{ stat[2] }}</span>
                        </div>
                    </div>
                    {% endfor %}
                </div>
                {% else %}
                <p class="text-muted">No complaint data available</p>
                {% endif %}
            </div>
        </div>

        <div class="col-md-6">
            <div class="dashboard-card">
                <h4 class="mb-4">Sentiment Trends</h4>
                {% if sentiment_trends %}
                <div class="list-group">
                    {% for trend in sentiment_trends[:10] %}
                    <div class="list-group-item">
                        <div class="d-flex justify-content-between align-items-center">
                            <span>
                                {{ trend[0] }} - {{ trend[1]|title }}
                            </span>
                            <span class="badge bg-{{ 'success' if trend[1] == 'positive' else 'danger' if trend[1] == 'negative' else 'secondary' }}">
                                {{ trend[2] }}
                            </span>
                        </div>
                    </div>
                    {% endfor %}
                </div>
                {% else %}
                <p class="text-muted">No sentiment data available</p>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}