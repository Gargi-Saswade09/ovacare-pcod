import {Pie} from "react-chartjs-2"

function RiskChart({score}){

const data={
labels:["Risk","Safe"],
datasets:[
{
data:[score,100-score]
}
]
}

return <Pie data={data}/>

}

export default RiskChart