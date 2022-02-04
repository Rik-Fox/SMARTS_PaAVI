import React, { useState } from "react";
import { Route, Switch } from "react-router-dom";
import { Layout, Select, Space, Button, Checkbox } from "antd";
import { LoadingOutlined } from "@ant-design/icons";
import ReactDOM from 'react-dom';

const styles = StyleSheet.create({

    loginButtonSection: {
        width: '100%',
        height: '30%',
        justifyContent: 'center',
        alignItems: 'center'
    }
}
)

class ClickToStart extends React.Component {
    onClick() {
        alert('AAAAAAAAHHH!!!!!');
    }

    render() {
        return <button onClick={this.onClick}>Click here to start.</button>
    }
}


export default function StartScreen({
    simID
}) {
    // console.log(worldState)
    let currentSimID = null

    // if (currentSimID === simID) {
    //     return;
    // }
    // else {
    ReactDOM.render(
        // <div
        //     style={{
        //         display: "flex",
        //         width: "100%",
        //         height: "100%",
        //         flexDirection: "column",
        //     }}
        // >
        <ClickToStart />,
        // </div>,
        document.getElementById('root')
    )
    currentSimID = simID
    return;
    // }

    return
    // return (
    //     <Header>
    //         <Space>
    //             <Select
    //                 value={selectValue}
    //                 style={{ width: 400 }}
    //                 onChange={(value) => onSelectSimulation(value)}
    //             >
    //                 <Option value="all">All Simulations</Option>
    //                 <OptGroup label="Simulations">
    //                     {simulationIds.map((id) => (
    //                         <Option key={id} value={id}>{`Sim ${displaySimName(id)}`}</Option>
    //                     ))}
    //                 </OptGroup>
    //             </Select>

    //             <Switch>
    //                 <Route exact={true} path="/all"></Route>
    //                 <Route path="/:simulation">
    //                     <Button
    //                         type="primary"
    //                         danger
    //                         icon={recording ? <LoadingOutlined /> : null}
    //                         onClick={toggleRecording}
    //                     >
    //                         Record
    //                     </Button>
    //                 </Route>
    //             </Switch>
    //         </Space>

    //         <Space style={{ float: "right" }}>
    //             <Select
    //                 defaultValue={PLAYMODES.near_real_time}
    //                 onChange={(mode) => onSelectPlayingMode(mode)}
    //             >
    //                 <Option value={PLAYMODES.near_real_time}>Near Realtime Mode</Option>
    //                 <Option value={PLAYMODES.uncapped}>Uncapped Mode</Option>
    //             </Select>
    //             <Checkbox defaultChecked onClick={toggleShowControls}>
    //                 Show Controls
    //             </Checkbox>
    //             <Checkbox onClick={toggleEgoView}>Egocentric View</Checkbox>
    //         </Space>
    //     </Header>
    // );
}