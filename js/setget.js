import { app } from "../../scripts/app.js";

//based on diffus3's SetGet: https://github.com/diffus3/ComfyUI-extensions


// メニュー設定テスト(未実装)
let disablePrefix = app.ui.settings.getSettingValue("KANI-Nodes.disablePrefix")
console.log("★★★disablePrefix: ", disablePrefix)
console.log("★★★KJ?: ", app.ui.settings.getSettingValue("KJNodes.disablePrefix"))
console.log("★★★autocolor?: ", app.ui.settings.getSettingValue("KJNodes.nodeAutoColor"))


console.log(LGraphCanvas.node_colors)
// Nodes that allow you to tunnel connections for cleaner graphs
function setColorAndBgColor(type) {
    const colorMap = {
        "DEFAULT": { color: undefined, bgcolor: undefined},
        "MODEL": LGraphCanvas.node_colors.blue,
        "LATENT": LGraphCanvas.node_colors.purple,
        "VAE": LGraphCanvas.node_colors.red,
        "CONDITIONING": LGraphCanvas.node_colors.brown,
        "IMAGE": LGraphCanvas.node_colors.pale_blue,
        "CLIP": LGraphCanvas.node_colors.yellow,
        "FLOAT": LGraphCanvas.node_colors.green,
        "STRING": { color: "#255A1D", bgcolor: "#2F7024"},
        "MASK": { color: "#1c5715", bgcolor: "#1f401b"},
        "INT": { color: "#1b4669", bgcolor: "#29699c"},
        "CONTROL_NET": { color: "#156653", bgcolor: "#1c453b"},
        "NOISE": { color: "#2e2e2e", bgcolor: "#242121"},
        "GUIDER": { color: "#3c7878", bgcolor: "#1c453b"},
        "SAMPLER": { color: "#614a4a", bgcolor: "#3b2c2c"},
        "SIGMAS": { color: "#485248", bgcolor: "#272e27"},

    };

    const colors = colorMap[type];
    if (colors) {
        this.color = colors.color;
        this.bgcolor = colors.bgcolor;
    }
}

const LGraphNode = LiteGraph.LGraphNode

function showAlert(message) {
  app.extensionManager.toast.add({
    severity: 'warn',
    summary: "KANI Get/Set",
    detail: `${message}. Most likely you're missing custom nodes`,
    life: 5000,
  })
}
app.registerExtension({
  name: "🦀SetNode",
  registerCustomNodes() {
    class SetNode extends LGraphNode {
      defaultVisibility = true;
      serialize_widgets = true;
      drawConnection = false;
      currentGetters = null;
      slotColor = "#FFF";
      canvas = app.canvas;
      menuEntry = "Show connections";

      constructor(title) {
        super(title)
        if (!this.properties) {
          this.properties = {
            "previousName": ""
          };
        }
        this.properties.showOutputText = SetNode.defaultVisibility;

        const node = this;

        this.addWidget(
          "text",
          "Constant",
          '',
          (s, t, u, v, x) => {
            node.validateName(node.graph);
            if(this.widgets[0].value !== ''){
              this.title = (!disablePrefix ? "🦀Set_" : "") + this.widgets[0].value;
            }
            this.update();
            this.properties.previousName = this.widgets[0].value;
          },
          {}
        )

        this.addInput("*", "*");
        this.addOutput("*", '*');

        this.onConnectionsChange = function(
          slotType,  //1 = input, 2 = output
          slot,
          isChangeConnect,
                    link_info,
                    output
        ) {
          //On Disconnect
          console.log(arguments);
          console.log("this.inputs[slot]", this.inputs[slot]);
          if (slotType == 1 && !isChangeConnect) {
            // if(this.inputs[slot].name === ''){
              this.inputs[slot].type = '*';
              this.inputs[slot].name = '*';
              this.title = "🦀SetNode"
              setColorAndBgColor.call(this, "DEFAULT");
            // }
          }
          if (slotType == 2 && !isChangeConnect) {
            this.outputs[slot].type = '*';
            this.outputs[slot].name = '*';

          }
          //On Connect
          if (link_info && node.graph && slotType == 1 && isChangeConnect) {
            console.log("link_info: ", link_info)
            const fromNode = node.graph._nodes.find((otherNode) => otherNode.id == link_info.origin_id);

            if (fromNode && fromNode.outputs && fromNode.outputs[link_info.origin_slot]) {
              const type = fromNode.outputs[link_info.origin_slot].type;

              if (this.title === "🦀SetNode"){
                this.title = (!disablePrefix ? "🦀Set_" : "") + type;
              }
              if (this.widgets[0].value === '*'){
                this.widgets[0].value = type
              }

              this.validateName(node.graph);
              this.inputs[0].type = type;
              this.inputs[0].name = type;

              // if (app.ui.settings.getSettingValue("KJNodes.nodeAutoColor")){
              //   setColorAndBgColor.call(this, type);
              // }
              // 無条件で色を変える
              console.log("★★★", this);
              if(fromNode.color != undefined && fromNode.bgcolor != undefined){
                this.color = fromNode.color;
                this.bgcolor = fromNode.bgcolor;
              }else{
                setColorAndBgColor.call(this, type);
              }
            } else {
                showAlert("node input undefined.")
            }
          }
          if (link_info && node.graph && slotType == 2 && isChangeConnect) {
            const fromNode = node.graph._nodes.find((otherNode) => otherNode.id == link_info.origin_id);

            if (fromNode && fromNode.inputs && fromNode.inputs[link_info.origin_slot]) {
              const type = fromNode.inputs[link_info.origin_slot].type;

              this.outputs[0].type = type;
              this.outputs[0].name = type;
            } else {
              showAlert('node output undefined');
            }
          }


          //Update either way
          this.update();
        }

        this.validateName = function(graph) {
          let widgetValue = node.widgets[0].value;

          if (widgetValue !== '') {
            let tries = 0;
            const existingValues = new Set();

            graph._nodes.forEach(otherNode => {
              if (otherNode !== this && otherNode.type === '🦀SetNode') {
                existingValues.add(otherNode.widgets[0].value);
              }
            });

            while (existingValues.has(widgetValue)) {
              widgetValue = node.widgets[0].value + "_" + tries;
              tries++;
            }

            node.widgets[0].value = widgetValue;
            this.update();
          }
        }

        this.clone = function () {
          const cloned = SetNode.prototype.clone.apply(this);
          cloned.inputs[0].name = '*';
          cloned.inputs[0].type = '*';
          cloned.value = '';
          cloned.properties.previousName = '';
          cloned.size = cloned.computeSize();
          return cloned;
        };

        this.onAdded = function(graph) {
          this.validateName(graph);
        }


        this.update = function() {
          if (!node.graph) {
            return;
          }

          const getters = this.findGetters(node.graph);



          getters.forEach(getter => {
            getter.setType(this.inputs[0].type);
          });

          if (this.widgets[0].value) {
            const gettersWithPreviousName = this.findGetters(node.graph, true);
            gettersWithPreviousName.forEach(getter => {
              getter.setName(this.widgets[0].value);
            });
          }

          const allGetters = node.graph._nodes.filter(otherNode => otherNode.type === "🦀GetNode");
          allGetters.forEach(otherNode => {
            if (otherNode.setComboValues) {
              otherNode.setComboValues();
            }
          });
        }


        this.findGetters = function(graph, checkForPreviousName) {
          const name = checkForPreviousName ? this.properties.previousName : this.widgets[0].value;
          return graph._nodes.filter(otherNode => otherNode.type === '🦀GetNode' && otherNode.widgets[0].value === name && name !== '');
        }


        // This node is purely frontend and does not impact the resulting prompt so should not be serialized
        this.isVirtualNode = true;
      }


      onRemoved() {
        const allGetters = this.graph._nodes.filter((otherNode) => otherNode.type == "🦀GetNode");
        allGetters.forEach((otherNode) => {
          if (otherNode.setComboValues) {
            otherNode.setComboValues([this]);
          }
        })
      }

      onDrawForeground(ctx, lGraphCanvas) {
        if (this.drawConnection) {
          this._drawVirtualLinks(lGraphCanvas, ctx);
        }
      }
      _drawVirtualLinks(lGraphCanvas, ctx) {
        if (!this.currentGetters?.length) return;
        var title = this.getTitle ? this.getTitle() : this.title;
        var title_width = ctx.measureText(title).width;
        if (!this.flags.collapsed) {
          var start_node_slotpos = [
            this.size[0],
            LiteGraph.NODE_TITLE_HEIGHT * 0.5,
            ];
        }
        else {

          var start_node_slotpos = [
            title_width + 55,
            -15,

            ];
        }
        // Provide a default link object with necessary properties, to avoid errors as link can't be null anymore
        const defaultLink = { type: 'default', color: this.slotColor };

        for (const getter of this.currentGetters) {
          if (!this.flags.collapsed) {
          var end_node_slotpos = this.getConnectionPos(false, 0);
          end_node_slotpos = [
            getter.pos[0] - end_node_slotpos[0] + this.size[0],
            getter.pos[1] - end_node_slotpos[1]
            ];
          }
          else {
            var end_node_slotpos = this.getConnectionPos(false, 0);
            end_node_slotpos = [
            getter.pos[0] - end_node_slotpos[0] + title_width + 50,
            getter.pos[1] - end_node_slotpos[1] - 30
            ];
          }
          // renderLink ( Vec2: a, Vec2: b, Object: link, Boolean: skip_border, Boolean: flow, String: color, Number: start_dir,  Number: end_dir, Number: num_sublines )
          /*
          a Vec2
          start pos

          b Vec2
          end pos

          link Object
          the link object with all the link info

          skip_border Boolean
          ignore the shadow of the link

          flow Boolean
          show flow animation (for events)

          color String
          the color for the link

          start_dir Number
          the direction enum

          end_dir Number
          the direction enum

          num_sublines Number
          number of sublines (useful to represent vec3 or rgb)
          */
          lGraphCanvas.renderLink(
            ctx,
            start_node_slotpos,
            end_node_slotpos,
            defaultLink,
            false,
            null,
            this.slotColor,
            LiteGraph.RIGHT,
            LiteGraph.LEFT
          );
        }
      }
    }

    LiteGraph.registerNodeType(
      "🦀SetNode",
      Object.assign(SetNode, {
        title: "🦀Set",
      })
    );

    SetNode.category = "KANI-NODES";
  },
});


app.registerExtension({
  name: "🦀GetNode",
  registerCustomNodes() {
    class GetNode extends LGraphNode {

      defaultVisibility = true;
      serialize_widgets = true;
      drawConnection = false;
      slotColor = "#FFF";
      currentSetter = null;
      canvas = app.canvas;

      constructor(title) {
        super(title)
        if (!this.properties) {
          this.properties = {};
        }
        this.properties.showOutputText = GetNode.defaultVisibility;
        const node = this;
        this.addWidget(
          "combo",
          "Constant",
          "",
          (e) => {
            this.onRename();
          },
          {
            values: () => {
                            const setterNodes = node.graph._nodes.filter((otherNode) => otherNode.type == '🦀SetNode');
                            return setterNodes.map((otherNode) => otherNode.widgets[0].value).sort();
                        }
          }
        )

        this.addOutput("*", '*');
        this.onConnectionsChange = function(
          slotType,  //0 = output, 1 = input
          slot,  //self-explanatory
          isChangeConnect,
                    link_info,
                    output
        ) {
          this.validateLinks();
        }

        this.setName = function(name) {
          node.widgets[0].value = name;
          node.onRename();
          node.serialize();
        }

        // valueが変更されたときに呼び出される
        this.onRename = function() {
          const setter = this.findSetter(node.graph);
          if (setter) {
            let linkType = (setter.inputs[0].type);

            this.setType(linkType);
            this.title = (!disablePrefix ? "🦀Get_" : "") + setter.widgets[0].value;

            console.log("★onRename: ", setter);

            // if (app.ui.settings.getSettingValue("KJNodes.nodeAutoColor")){
            //   setColorAndBgColor.call(this, linkType);
            // }
            // 無条件で色を変える
            this.color = setter.color;
            this.bgcolor = setter.bgcolor;
        } else {
            this.setType('*');
          }
        }

        this.clone = function () {
          const cloned = GetNode.prototype.clone.apply(this);
          cloned.size = cloned.computeSize();
          return cloned;
        };

        this.validateLinks = function() {
          if (this.outputs[0].type !== '*' && this.outputs[0].links) {
            this.outputs[0].links.filter(linkId => {
              const link = node.graph.links[linkId];
              return link && (link.type !== this.outputs[0].type && link.type !== '*');
            }).forEach(linkId => {
              node.graph.removeLink(linkId);
            });
          }
        };

        this.setType = function(type) {
          this.outputs[0].name = type;
          this.outputs[0].type = type;
          this.validateLinks();
        }

        this.findSetter = function(graph) {
          const name = this.widgets[0].value;
          const foundNode = graph._nodes.find(otherNode => otherNode.type === '🦀SetNode' && otherNode.widgets[0].value === name && name !== '');
          return foundNode;
        };

        this.goToSetter = function() {
          const setter = this.findSetter(this.graph);
          this.canvas.centerOnNode(setter);
          this.canvas.selectNode(setter, false);
        };

        // This node is purely frontend and does not impact the resulting prompt so should not be serialized
        this.isVirtualNode = true;
      }

      getInputLink(slot) {
        const setter = this.findSetter(this.graph);

        console.log("setter: ", setter);

        if (setter) {
          const slotInfo = setter.inputs[slot];
          const link = this.graph.links[slotInfo.link];
          return link;
        } else {
          const errorMessage = "No SetNode found for " + this.widgets[0].value + "(" + this.type + ")";
          showAlert(errorMessage);
          //throw new Error(errorMessage);
        }
      }
      onAdded(graph) {
      }
      onDrawForeground(ctx, lGraphCanvas) {
        if (this.drawConnection) {
          this._drawVirtualLink(lGraphCanvas, ctx);
        }
      }
      // onDrawCollapsed(ctx, lGraphCanvas) {
      //   if (this.drawConnection) {
      //     this._drawVirtualLink(lGraphCanvas, ctx);
      //   }
      // }
      _drawVirtualLink(lGraphCanvas, ctx) {
        if (!this.currentSetter) return;

        // Provide a default link object with necessary properties, to avoid errors as link can't be null anymore
        const defaultLink = { type: 'default', color: this.slotColor };

        let start_node_slotpos = this.currentSetter.getConnectionPos(false, 0);
        start_node_slotpos = [
          start_node_slotpos[0] - this.pos[0],
          start_node_slotpos[1] - this.pos[1],
        ];
        let end_node_slotpos = [0, -LiteGraph.NODE_TITLE_HEIGHT * 0.5];
        lGraphCanvas.renderLink(
          ctx,
          start_node_slotpos,
          end_node_slotpos,
          defaultLink,
          false,
          null,
          this.slotColor
        );
      }
    }

    LiteGraph.registerNodeType(
      "🦀GetNode",
      Object.assign(GetNode, {
        title: "🦀Get",
      })
    );

    GetNode.category = "KANI-NODES";
  },
});
