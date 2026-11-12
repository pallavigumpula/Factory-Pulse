/**
 * FactoryPulse — Industrial Charts Wrapper (Plotly.js)
 */

const Charts = {
    theme: {
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        primary: "#2563eb",
        success: "#10b981",
        warning: "#f59e0b",
        danger: "#ef4444",
        secondary: "#64748b",
        dark: "#0f172a"
    },

    renderOEETrendChart(elementId, trendData) {
        if (!trendData || trendData.length === 0) return;
        const dates = trendData.map(d => d.date);
        const oeeVals = trendData.map(d => d.oee);
        const availVals = trendData.map(d => d.availability);
        const perfVals = trendData.map(d => d.performance);
        const qualVals = trendData.map(d => d.quality);

        const traces = [
            {
                x: dates,
                y: oeeVals,
                name: "OEE %",
                type: "scatter",
                mode: "lines+markers",
                line: { color: "#2563eb", width: 3 }
            },
            {
                x: dates,
                y: availVals,
                name: "Availability %",
                type: "scatter",
                mode: "lines",
                line: { color: "#10b981", width: 1.5, dash: "dot" }
            },
            {
                x: dates,
                y: perfVals,
                name: "Performance %",
                type: "scatter",
                mode: "lines",
                line: { color: "#f59e0b", width: 1.5, dash: "dash" }
            },
            {
                x: dates,
                y: qualVals,
                name: "Quality %",
                type: "scatter",
                mode: "lines",
                line: { color: "#06b6d4", width: 1.5 }
            }
        ];

        const layout = {
            margin: { t: 20, r: 20, b: 40, l: 45 },
            height: 320,
            hovermode: "x unified",
            xaxis: { gridcolor: "#f1f5f9" },
            yaxis: { range: [0, 105], gridcolor: "#f1f5f9", title: "Percentage (%)" },
            legend: { orientation: "h", y: -0.2, x: 0.1 },
            paper_bgcolor: "transparent",
            plot_bgcolor: "transparent"
        };

        Plotly.newPlot(elementId, traces, layout, { responsive: true, displayModeBar: false });
    },

    renderOEEByMachineChart(elementId, machineData) {
        if (!machineData || machineData.length === 0) return;
        // Sort descending by OEE
        const sorted = [...machineData].sort((a, b) => a.oee - b.oee);
        const codes = sorted.map(m => m.machine_code);
        const oeeVals = sorted.map(m => m.oee);
        const colors = sorted.map(m => m.oee >= 85.0 ? "#10b981" : (m.oee >= 70.0 ? "#f59e0b" : "#ef4444"));

        const trace = {
            y: codes,
            x: oeeVals,
            type: "bar",
            orientation: "h",
            marker: { color: colors },
            text: oeeVals.map(v => `${v}%`),
            textposition: "auto"
        };

        const layout = {
            margin: { t: 20, r: 25, b: 35, l: 70 },
            height: Math.max(300, codes.length * 24),
            xaxis: { range: [0, 100], gridcolor: "#f1f5f9", title: "OEE (%)" },
            yaxis: { automargin: true },
            paper_bgcolor: "transparent",
            plot_bgcolor: "transparent",
            shapes: [
                {
                    type: "line",
                    x0: 85,
                    x1: 85,
                    y0: -0.5,
                    y1: codes.length - 0.5,
                    line: { color: "#2563eb", width: 2, dash: "dash" }
                }
            ]
        };

        Plotly.newPlot(elementId, [trace], layout, { responsive: true, displayModeBar: false });
    },

    renderOEEByLineChart(elementId, lineData) {
        if (!lineData || lineData.length === 0) return;
        const labels = lineData.map(l => l.line_code);
        const oee = lineData.map(l => l.oee);
        const target = lineData.map(l => l.target_oee);

        const traces = [
            {
                x: labels,
                y: oee,
                name: "Actual OEE",
                type: "bar",
                marker: { color: "#2563eb" },
                text: oee.map(v => `${v}%`),
                textposition: "auto"
            },
            {
                x: labels,
                y: target,
                name: "Target OEE",
                type: "bar",
                marker: { color: "#cbd5e1" },
                text: target.map(v => `${v}%`),
                textposition: "auto"
            }
        ];

        const layout = {
            barmode: "group",
            margin: { t: 20, r: 20, b: 40, l: 45 },
            height: 320,
            yaxis: { range: [0, 100], gridcolor: "#f1f5f9" },
            legend: { orientation: "h", y: -0.2 },
            paper_bgcolor: "transparent",
            plot_bgcolor: "transparent"
        };

        Plotly.newPlot(elementId, traces, layout, { responsive: true, displayModeBar: false });
    },

    renderDowntimeParetoChart(elementId, downtimeData) {
        if (!downtimeData || downtimeData.length === 0) return;
        const topReasons = downtimeData.slice(0, 8);
        const names = topReasons.map(d => d.name);
        const minutes = topReasons.map(d => d.duration_minutes);
        const colors = topReasons.map(d => d.is_planned ? "#64748b" : "#ef4444");

        const trace = {
            x: minutes,
            y: names,
            type: "bar",
            orientation: "h",
            marker: { color: colors },
            text: minutes.map(m => `${m} min`),
            textposition: "auto"
        };

        const layout = {
            margin: { t: 20, r: 25, b: 35, l: 180 },
            height: 320,
            yaxis: { automargin: true, autorange: "reversed" },
            xaxis: { gridcolor: "#f1f5f9", title: "Downtime (Minutes)" },
            paper_bgcolor: "transparent",
            plot_bgcolor: "transparent"
        };

        Plotly.newPlot(elementId, [trace], layout, { responsive: true, displayModeBar: false });
    },

    renderStatusDistributionChart(elementId, machines) {
        if (!machines || machines.length === 0) return;
        const counts = {};
        machines.forEach(m => {
            counts[m.current_status] = (counts[m.current_status] || 0) + 1;
        });

        const colorMap = {
            RUNNING: "#10b981",
            STOPPED: "#ef4444",
            IDLE: "#f59e0b",
            BREAK: "#6366f1",
            MAINTENANCE: "#ea580c",
            CHANGEOVER: "#a855f7"
        };

        const labels = Object.keys(counts);
        const values = Object.values(counts);
        const colors = labels.map(l => colorMap[l] || "#94a3b8");

        const trace = {
            labels,
            values,
            type: "pie",
            hole: 0.55,
            marker: { colors },
            textinfo: "label+value"
        };

        const layout = {
            margin: { t: 10, r: 10, b: 10, l: 10 },
            height: 280,
            showlegend: false,
            paper_bgcolor: "transparent"
        };

        Plotly.newPlot(elementId, [trace], layout, { responsive: true, displayModeBar: false });
    },

    renderGoodVsScrapChart(elementId, goodCount, scrapCount, reworkCount) {
        const trace = {
            labels: ["Good Pieces", "Scrap Pieces", "Rework Pieces"],
            values: [goodCount, scrapCount, reworkCount],
            type: "pie",
            hole: 0.6,
            marker: { colors: ["#10b981", "#ef4444", "#f59e0b"] },
            textinfo: "label+percent"
        };

        const layout = {
            margin: { t: 10, r: 10, b: 10, l: 10 },
            height: 280,
            showlegend: false,
            paper_bgcolor: "transparent"
        };

        Plotly.newPlot(elementId, [trace], layout, { responsive: true, displayModeBar: false });
    }
};
