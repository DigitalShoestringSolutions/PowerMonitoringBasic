import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Colors,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import APIBackend from './RestAPI'

import * as dayjs from 'dayjs'
import * as weekOfYear from 'dayjs/plugin/weekOfYear';
import * as advancedFormat from 'dayjs/plugin/advancedFormat';

import './app.css'

dayjs.extend(weekOfYear)
dayjs.extend(advancedFormat)

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Colors,
  Legend
);


export const options = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top',
    },
    // title: {
    //   display: true,
    //   text: 'Chart.js Line Chart',
    // },
  },
  interaction: {
    axis: "x",
    mode: "nearest",
    intersect: false,
  }
};

function App() {
  let [loaded, setLoaded] = React.useState(false)
  let [pending, setPending] = React.useState(false)
  let [error, setError] = React.useState(null)
  let [config, setConfig] = React.useState(undefined)

  React.useEffect(() => {
    const do_load = async () => {
      setPending(true)
      APIBackend.api_get('http://' + document.location.host + '/config/config.json').then((response) => {
        if (response.status === 200) {
          console.log("config ", response.payload)
          setConfig(response.payload)
          setLoaded(true)
        } else {
          console.log("ERROR LOADING CONFIG")
          setError("ERROR: Unable to load configuration!")
        }
      }).catch((err) => {
        console.error(err.message);
        setError("ERROR: Unable to load configuration!")
      })
    }

    if (!loaded && !pending) {
      do_load()
    }
  }, [loaded, pending])

  if (!loaded) {
    return error ? error : "Loading..."
  }

  return (
    <Graph config={config} />
  );
}

function Graph({ config }) {
  let [loaded, setLoaded] = React.useState(false)
  let [pending, setPending] = React.useState(false)
  let [error, setError] = React.useState(null)

  let [data, setData] = React.useState({})
  let [period, setPeriod] = React.useState(undefined)

  React.useEffect(() => {
    const do_load = async () => {
      setPending(true)

      let params = new URLSearchParams(window.location.search);
      setPeriod(params.get("period"))

      let url = (config.source.host ? config.source.host : window.location.hostname) + (config.source.port ? ":" + config.source.port : "")
      let path = window.location.pathname
      APIBackend.api_get('http://' + url + path + "?" + params.toString()).then((response) => {
        if (response.status === 200) {
          console.log("payload", response.payload)
          setData(response.payload)
          setLoaded(true)
        } else {
          console.log("ERROR LOADING DATA")
          setError("ERROR: Unable to load data!")
        }
      }).catch((err) => {
        console.error(err.message);
        setError("ERROR: Unable to load data!")
      })
    }

    if (!loaded && !pending) {
      do_load()
    }
  }, [config, loaded, pending])

  if (!loaded) {
    return error ? error : "Loading..."
  }

  let out = {}
  let x = []
  let series = []

  const formats = {
    '10m': {
      x_index: (d) => Math.ceil(d.minute() / 10) * 10,
      x_label: "mm",
      s_index: "DD/MM/YY HH",
      s_label: "HH:00 ddd DD/MM "
    },
    '1h': {
      x_index: (d) => d.hour(),
      x_label: "HH:00",
      s_index: "DD/MM/YY",
      s_label: "ddd DD/MM"
    },
    '1d': {
      x_index: (d) => d.day(),
      x_label: "ddd",
      s_index: "w",
      s_label: "[week] w"
    },
    '1w': {
      x_index: (d) => d.week(),
      x_label: "[week] w",
      s_index: "YY",
      s_label: "YYYY"
    }
  }

  data.forEach(entry => {
    let d = dayjs(entry._time)
    let x_index = formats[period].x_index(d)
    let x_label = d.format(formats[period].x_label)
    let series_index = d.format(formats[period].s_index)
    let series_label = d.format(formats[period].s_label)
    let s_entry = out[x_index]

    if (s_entry === undefined) {
      s_entry = {}
      out[x_index] = s_entry
    }
    s_entry[series_index] = entry._value

    if (x.findIndex(elem => elem.index === x_index) === -1) {
      x.push({ index: x_index, label: x_label })
    }

    if (series.findIndex(elem => elem.index === series_index) === -1) {
      series.push({ index: series_index, label: series_label })
    }
  });

  let x_sorted = x.sort((a, b) => a.index - b.index)
  // let series_sorted = series.sort((a, b) => a.index - b.index)
  let series_sorted = series

  console.log(series)

  let graph_data = {
    labels: x_sorted.map(entry => entry.label),
    datasets: series_sorted.map(s_entry => ({
      label: s_entry.label,
      data: x_sorted.map(x_entry => out[x_entry.index] ? out[x_entry.index][s_entry.index] : undefined),
      borderWidth: 1
    }))
  };

  return (
    <Line options={options} data={graph_data} />
  );
}


export default App;

